# -*- coding: utf-8 -*-
import base64
import re
import uuid
from datetime import datetime
from xml.sax.saxutils import escape

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


PAIN001_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>{msg_id}</MsgId>
      <CreDtTm>{cre_dt_tm}</CreDtTm>
      <NbOfTxs>{nb_txs}</NbOfTxs>
      <CtrlSum>{ctrl_sum:.2f}</CtrlSum>
      <InitgPty><Nm>{debtor_name}</Nm></InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>{pmt_inf_id}</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <NbOfTxs>{nb_txs}</NbOfTxs>
      <CtrlSum>{ctrl_sum:.2f}</CtrlSum>
      <ReqdExctnDt>{reqd_date}</ReqdExctnDt>
      <Dbtr><Nm>{debtor_name}</Nm></Dbtr>
      <DbtrAcct><Id><IBAN>{debtor_iban}</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId>{debtor_bic_xml}</FinInstnId></DbtrAgt>
      <ChrgBr>SLEV</ChrgBr>
{txs}
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>
"""


def _clean_iban(iban):
    return (iban or "").replace(" ", "").upper()


def _valid_iban(iban):
    iban = _clean_iban(iban)
    if not re.match(r"^[A-Z]{2}[0-9A-Z]{13,32}$", iban):
        return False
    # mod97 check
    rearranged = iban[4:] + iban[:4]
    num = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    try:
        return int(num) % 97 == 1
    except Exception:
        return False


class SctBatch(models.Model):
    _name = "sct.batch"
    _description = "Lot de virements SEPA (SCT)"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Référence", required=True, copy=False, default="Nouveau")
    company_id = fields.Many2one(
        "res.company", string="Société", required=True, default=lambda s: s.env.company)
    journal_id = fields.Many2one(
        "account.journal", string="Journal bancaire", required=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]")
    date = fields.Date(string="Date d'exécution", required=True, default=fields.Date.context_today)
    state = fields.Selection([
        ("draft", "Brouillon"),
        ("generated", "Fichier généré"),
        ("sent", "Transmis"),
        ("rejected", "Rejets reçus"),
    ], string="État", default="draft", tracking=True)
    payment_ids = fields.Many2many(
        "account.payment", string="Paiements",
        domain="[('payment_type', '=', 'outbound'), ('state', '=', 'posted'),"
               " ('company_id', '=', company_id)]")
    msg_id = fields.Char(string="Identifiant message (MsgId)", copy=False)
    pmt_inf_id = fields.Char(string="Identifiant lot (PmtInfId)", copy=False)
    file_data = fields.Binary(string="Fichier pain.001", readonly=True, copy=False)
    file_name = fields.Char(string="Nom du fichier", readonly=True, copy=False)
    nb_txs = fields.Integer(string="Nombre de transactions", compute="_compute_totals", store=True)
    ctrl_sum = fields.Monetary(string="Montant total", compute="_compute_totals",
                               currency_field="currency_id", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    note = fields.Text(string="Notes")
    reject_info = fields.Text(string="Informations rejets (pain.002)", readonly=True)

    @api.depends("payment_ids.amount", "payment_ids")
    def _compute_totals(self):
        for batch in self:
            batch.nb_txs = len(batch.payment_ids)
            batch.ctrl_sum = sum(batch.payment_ids.mapped("amount"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "Nouveau") == "Nouveau":
                vals["name"] = self.env["ir.sequence"].next_by_code("sct.batch") or "SCT/%s" % fields.Date.today()
        return super().create(vals_list)

    def _debtor_bank(self):
        self.ensure_one()
        bank = self.journal_id.bank_account_id
        bank_acc = getattr(bank, "acc_number", False) or getattr(bank, "account_number", False) if bank else False
        if not bank or not bank_acc:
            raise UserError("Le journal bancaire doit avoir un compte bancaire (IBAN) configuré.")
        iban = _clean_iban(bank_acc)
        if not _valid_iban(iban):
            raise UserError("L'IBAN du journal (%s) est invalide." % bank_acc)
        bic = (bank.bank_bic or "").strip().upper()
        return bank, iban, bic

    def _creditor_party(self, payment):
        partner = payment.partner_id
        bank = payment.partner_bank_id
        bank_acc = getattr(bank, "acc_number", False) or getattr(bank, "account_number", False) if bank else False
        if not bank or not bank_acc:
            raise UserError("Paiement %s : aucun compte bancaire (IBAN) du bénéficiaire %s." % (
                payment.name, partner.display_name))
        iban = _clean_iban(bank_acc)
        if not _valid_iban(iban):
            raise UserError("Paiement %s : IBAN bénéficiaire invalide (%s)." % (payment.name, bank_acc))
        bic = (bank.bank_bic or "").strip().upper()
        return partner, iban, bic

    def _tx_block(self, idx, payment):
        partner, iban, bic = self._creditor_party(payment)
        bic_xml = "<BIC>%s</BIC>" % escape(bic) if bic else "<Othr><Id>NOTPROVIDED</Id></Othr>"
        end_to_end = escape((payment.name or str(payment.id)).replace("/", "-")[:35])
        rmt = escape((payment.ref or payment.memo or payment.name or "")[:140])
        return f"""      <CdtTrfTxInf>
        <PmtId><EndToEndId>{end_to_end}</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="{escape(payment.currency_id.name)}">{payment.amount:.2f}</InstdAmt></Amt>
        <CdtrAgt><FinInstnId>{bic_xml}</FinInstnId></CdtrAgt>
        <Cdtr><Nm>{escape(partner.display_name[:70])}</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>{iban}</IBAN></Id></CdtrAcct>
        <RmtInf><Ustrd>{rmt}</Ustrd></RmtInf>
      </CdtTrfTxInf>"""

    def action_generate(self):
        for batch in self:
            if not batch.payment_ids:
                raise UserError("Ajoutez au moins un paiement au lot %s." % batch.name)
            if batch.state not in ("draft", "generated", "rejected"):
                raise UserError("Le lot %s ne peut pas être (re)généré dans l'état %s." % (batch.name, batch.state))
            bank, debtor_iban, debtor_bic = batch._debtor_bank()
            debtor_name = escape((batch.company_id.name or "Debtor")[:70])
            debtor_bic_xml = "<BIC>%s</BIC>" % escape(debtor_bic) if debtor_bic else "<Othr><Id>NOTPROVIDED</Id></Othr>"
            msg_id = batch.msg_id or ("SCT-%s-%s" % (batch.name.replace("/", "-"), uuid.uuid4().hex[:8]))[:35]
            pmt_inf_id = batch.pmt_inf_id or ("PMT-%s" % uuid.uuid4().hex[:10])[:35]
            txs = "\n".join(batch._tx_block(i, p) for i, p in enumerate(batch.payment_ids, 1))
            xml = PAIN001_HEADER.format(
                msg_id=escape(msg_id),
                cre_dt_tm=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                nb_txs=len(batch.payment_ids),
                ctrl_sum=sum(batch.payment_ids.mapped("amount")),
                debtor_name=debtor_name,
                debtor_iban=debtor_iban,
                debtor_bic_xml=debtor_bic_xml,
                pmt_inf_id=escape(pmt_inf_id),
                reqd_date=batch.date.isoformat(),
                txs=txs,
            )
            fname = "pain001_%s_%s.xml" % (batch.name.replace("/", "-"), batch.date.isoformat())
            batch.write({
                "msg_id": msg_id,
                "pmt_inf_id": pmt_inf_id,
                "file_data": base64.b64encode(xml.encode("utf-8")),
                "file_name": fname,
                "state": "generated",
            })
        return True

    def action_mark_sent(self):
        self.filtered(lambda b: b.state == "generated").write({"state": "sent"})

    def action_reset_draft(self):
        self.write({"state": "draft", "file_data": False, "file_name": False, "msg_id": False, "pmt_inf_id": False})

    def action_download(self):
        self.ensure_one()
        if not self.file_data:
            raise UserError("Aucun fichier généré.")
        att = self.env["ir.attachment"].create({
            "name": self.file_name, "raw": (bytes(self.file_data) if (bytes(self.file_data or b"")[:1] == b"<") else base64.b64decode(self.file_data)), "type": "binary",
        })
        return {"type": "ir.actions.act_url", "url": "/web/content/%s?download=true" % att.id, "target": "self"}

    @api.constrains("payment_ids")
    def _check_payments(self):
        for batch in self:
            if batch.payment_ids.filtered(lambda p: p.payment_type != "outbound"):
                raise ValidationError("Seuls les paiements sortants sont autorisés dans un lot SCT.")
