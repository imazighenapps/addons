# -*- coding: utf-8 -*-
import base64
import uuid
from datetime import datetime
from xml.sax.saxutils import escape

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .sdd_mandate import _clean_iban, _valid_iban


PAIN008_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <CstmrDrctDbtInitn>
    <GrpHdr>
      <MsgId>{msg_id}</MsgId>
      <CreDtTm>{cre_dt_tm}</CreDtTm>
      <NbOfTxs>{nb_txs}</NbOfTxs>
      <CtrlSum>{ctrl_sum:.2f}</CtrlSum>
      <InitgPty><Nm>{creditor_name}</Nm></InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>{pmt_inf_id}</PmtInfId>
      <PmtMtd>DD</PmtMtd>
      <NbOfTxs>{nb_txs}</NbOfTxs>
      <CtrlSum>{ctrl_sum:.2f}</CtrlSum>
      <PmtTpInf><SvcLvl><Cd>SEPA</Cd></SvcLvl><LclInstrm><Cd>{scheme}</Cd></LclInstrm><SeqTp>{seq_tp}</SeqTp></PmtTpInf>
      <ReqdColltnDt>{reqd_date}</ReqdColltnDt>
      <Cdtr><Nm>{creditor_name}</Nm></Cdtr>
      <CdtrAcct><Id><IBAN>{creditor_iban}</IBAN></Id></CdtrAcct>
      <CdtrAgt><FinInstnId>{creditor_bic_xml}</FinInstnId></CdtrAgt>
      <ChrgBr>SLEV</ChrgBr>
      <CdtrSchmeId><Id><PrvtId><Othr><Id>{creditor_id}</Id><SchmeNm><Prtry>SEPA</Prtry></SchmeNm></Othr></PrvtId></Id></CdtrSchmeId>
{txs}
    </PmtInf>
  </CstmrDrctDbtInitn>
</Document>
"""


class SddBatch(models.Model):
    _name = "sdd.batch"
    _description = "Lot de prélèvements SEPA (SDD)"
    _order = "collection_date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Référence", required=True, copy=False, default="Nouveau")
    company_id = fields.Many2one(
        "res.company", string="Société", required=True, default=lambda s: s.env.company)
    journal_id = fields.Many2one(
        "account.journal", string="Journal bancaire", required=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]")
    collection_date = fields.Date(string="Date de prélèvement", required=True, default=fields.Date.context_today)
    scheme = fields.Selection([("CORE", "CORE"), ("B2B", "B2B")], default="CORE", required=True)
    sequence_type = fields.Selection([
        ("FRST", "FRST"), ("RCUR", "RCUR"), ("FNAL", "FNAL"), ("OOFF", "OOFF"),
    ], string="Séquence", required=True, default="RCUR")
    state = fields.Selection([
        ("draft", "Brouillon"),
        ("generated", "Fichier généré"),
        ("sent", "Transmis"),
        ("rejected", "Rejets reçus"),
    ], default="draft", tracking=True)
    line_ids = fields.One2many("sdd.batch.line", "batch_id", string="Lignes")
    msg_id = fields.Char(string="MsgId", copy=False)
    pmt_inf_id = fields.Char(string="PmtInfId", copy=False)
    creditor_identifier = fields.Char(
        string="Identifiant créancier SEPA (ICS)",
        help="Identifiant créancier SEPA fourni par la banque/autorité nationale.")
    file_data = fields.Binary(string="Fichier pain.008", readonly=True, copy=False)
    file_name = fields.Char(string="Nom du fichier", readonly=True, copy=False)
    nb_txs = fields.Integer(string="Nombre de transactions", compute="_compute_totals", store=True)
    ctrl_sum = fields.Monetary(string="Montant total", compute="_compute_totals",
                               currency_field="currency_id", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    reject_info = fields.Text(string="Informations rejets", readonly=True)

    @api.depends("line_ids.amount")
    def _compute_totals(self):
        for b in self:
            b.nb_txs = len(b.line_ids)
            b.ctrl_sum = sum(b.line_ids.mapped("amount"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "Nouveau") == "Nouveau":
                vals["name"] = self.env["ir.sequence"].next_by_code("sdd.batch") or "SDD/%s" % fields.Date.today()
        return super().create(vals_list)

    def _creditor_bank(self):
        self.ensure_one()
        bank = self.journal_id.bank_account_id
        bank_acc = getattr(bank, "acc_number", False) or getattr(bank, "account_number", False) if bank else False
        if not bank or not bank_acc:
            raise UserError("Le journal bancaire doit avoir un compte bancaire (IBAN) configuré.")
        iban = _clean_iban(bank_acc)
        if not _valid_iban(iban):
            raise UserError("L'IBAN du journal (%s) est invalide." % bank_acc)
        bic = (bank.bank_bic or "").strip().upper()
        return iban, bic

    def _tx_block(self, line):
        mandate = line.mandate_id
        partner = mandate.partner_id
        iban = _clean_iban(getattr(mandate.partner_bank_id, "acc_number", False) or getattr(mandate.partner_bank_id, "account_number", False))
        if not _valid_iban(iban):
            raise UserError("IBAN invalide pour le mandat %s." % mandate.name)
        bic = (mandate.partner_bank_id.bank_bic or "").strip().upper()
        bic_xml = "<BIC>%s</BIC>" % escape(bic) if bic else "<Othr><Id>NOTPROVIDED</Id></Othr>"
        end_to_end = escape((line.name or mandate.name)[:35])
        rmt = escape((line.communication or line.name or "")[:140])
        return f"""      <DrctDbtTxInf>
        <PmtId><EndToEndId>{end_to_end}</EndToEndId></PmtId>
        <InstdAmt Ccy="{escape(self.currency_id.name)}">{line.amount:.2f}</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>{escape(mandate.name[:35])}</MndtId>
            <DtOfSgntr>{mandate.signature_date.isoformat()}</DtOfSgntr>
          </MndtRltdInf>
        </DrctDbtTx>
        <DbtrAgt><FinInstnId>{bic_xml}</FinInstnId></DbtrAgt>
        <Dbtr><Nm>{escape(partner.display_name[:70])}</Nm></Dbtr>
        <DbtrAcct><Id><IBAN>{iban}</IBAN></Id></DbtrAcct>
        <RmtInf><Ustrd>{rmt}</Ustrd></RmtInf>
      </DrctDbtTxInf>"""

    def action_generate(self):
        for batch in self:
            if not batch.line_ids:
                raise UserError("Ajoutez au moins une ligne au lot %s." % batch.name)
            if not batch.creditor_identifier:
                raise UserError("Renseignez l'identifiant créancier SEPA (ICS) pour le lot %s." % batch.name)
            creditor_iban, creditor_bic = batch._creditor_bank()
            creditor_name = escape((batch.company_id.name or "Creditor")[:70])
            creditor_bic_xml = "<BIC>%s</BIC>" % escape(creditor_bic) if creditor_bic else "<Othr><Id>NOTPROVIDED</Id></Othr>"
            msg_id = batch.msg_id or ("SDD-%s-%s" % (batch.name.replace("/", "-"), uuid.uuid4().hex[:8]))[:35]
            pmt_inf_id = batch.pmt_inf_id or ("PMT-%s" % uuid.uuid4().hex[:10])[:35]
            # vérifier mandats actifs et schéma/séquence cohérents
            for line in batch.line_ids:
                m = line.mandate_id
                if m.state != "active":
                    raise UserError("Le mandat %s n'est pas actif." % m.name)
                if m.scheme != batch.scheme:
                    raise UserError("Le mandat %s (schéma %s) ne correspond pas au lot (%s)." % (m.name, m.scheme, batch.scheme))
            seq_tp = batch.sequence_type
            txs = "\n".join(batch._tx_block(l) for l in batch.line_ids)
            xml = PAIN008_HEADER.format(
                msg_id=escape(msg_id),
                cre_dt_tm=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                nb_txs=len(batch.line_ids),
                ctrl_sum=sum(batch.line_ids.mapped("amount")),
                creditor_name=creditor_name,
                creditor_iban=creditor_iban,
                creditor_bic_xml=creditor_bic_xml,
                creditor_id=escape(batch.creditor_identifier[:35]),
                pmt_inf_id=escape(pmt_inf_id),
                reqd_date=batch.collection_date.isoformat(),
                scheme=batch.scheme,
                seq_tp=seq_tp,
                txs=txs,
            )
            fname = "pain008_%s_%s.xml" % (batch.name.replace("/", "-"), batch.collection_date.isoformat())
            batch.write({
                "msg_id": msg_id, "pmt_inf_id": pmt_inf_id,
                "file_data": base64.b64encode(xml.encode("utf-8")),
                "file_name": fname, "state": "generated",
            })
            # mise à jour séquence des mandats
            batch.line_ids.mapped("mandate_id").consume_sequence()
        return True

    def action_mark_sent(self):
        self.filtered(lambda b: b.state == "generated").write({"state": "sent"})

    def action_download(self):
        self.ensure_one()
        if not self.file_data:
            raise UserError("Aucun fichier généré.")
        att = self.env["ir.attachment"].create({
            "name": self.file_name, "raw": (bytes(self.file_data) if (bytes(self.file_data or b"")[:1] == b"<") else base64.b64decode(self.file_data)), "type": "binary",
        })
        return {"type": "ir.actions.act_url", "url": "/web/content/%s?download=true" % att.id, "target": "self"}


class SddBatchLine(models.Model):
    _name = "sdd.batch.line"
    _description = "Ligne de prélèvement SDD"

    batch_id = fields.Many2one("sdd.batch", required=True, ondelete="cascade")
    name = fields.Char(string="Référence", required=True)
    mandate_id = fields.Many2one(
        "sdd.mandate", string="Mandat", required=True,
        domain="[('state', '=', 'active'), ('company_id', '=', parent.company_id)]")
    partner_id = fields.Many2one(related="mandate_id.partner_id", string="Débiteur", store=True)
    amount = fields.Monetary(string="Montant", required=True, currency_field="currency_id")
    currency_id = fields.Many2one(related="batch_id.currency_id")
    communication = fields.Char(string="Communication")
    invoice_id = fields.Many2one("account.move", string="Facture", domain="[('move_type', 'in', ('out_invoice','out_refund'))]")

    @api.constrains("amount")
    def _check_amount(self):
        for l in self:
            if l.amount <= 0:
                raise ValidationError("Le montant doit être strictement positif.")
