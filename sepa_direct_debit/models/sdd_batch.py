# -*- coding: utf-8 -*-
import base64
import uuid
from xml.sax.saxutils import escape

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from .sdd_mandate import _clean_iban, _is_valid_iban


PAIN008_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
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
      <PmtTpInf>
        <SvcLvl><Cd>SEPA</Cd></SvcLvl>
        <LclInstrm><Cd>{scheme}</Cd></LclInstrm>
        <SeqTp>{seq_tp}</SeqTp>
      </PmtTpInf>
      <ReqdColltnDt>{reqd_date}</ReqdColltnDt>
      <Cdtr><Nm>{creditor_name}</Nm></Cdtr>
      <CdtrAcct><Id><IBAN>{creditor_iban}</IBAN></Id></CdtrAcct>
      <CdtrAgt><FinInstnId>{creditor_bic_xml}</FinInstnId></CdtrAgt>
      <ChrgBr>SLEV</ChrgBr>
      <CdtrSchmeId>
        <Id><PrvtId><Othr><Id>{creditor_id}</Id><SchmeNm><Prtry>SEPA</Prtry></SchmeNm></Othr></PrvtId></Id>
      </CdtrSchmeId>
{txs}
    </PmtInf>
  </CstmrDrctDbtInitn>
</Document>
"""


class SddBatch(models.Model):
    _name = "sdd.batch"
    _description = "SEPA Direct Debit Batch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "collection_date desc, id desc"

    name = fields.Char(string="Reference", required=True, copy=False, default="New", tracking=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True,
        default=lambda self: self.env.company, index=True)
    currency_id = fields.Many2one(related="company_id.currency_id", store=True)
    journal_id = fields.Many2one(
        "account.journal", string="Bank Journal", required=True, tracking=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]")
    collection_date = fields.Date(
        string="Collection Date", required=True, default=fields.Date.context_today, tracking=True)
    scheme = fields.Selection([("CORE", "CORE"), ("B2B", "B2B")], required=True, default="CORE", tracking=True)
    sequence_type = fields.Selection([
        ("FRST", "First (FRST)"),
        ("RCUR", "Recurrent (RCUR)"),
        ("FNAL", "Final (FNAL)"),
        ("OOFF", "One-Off (OOFF)"),
    ], string="Sequence Type", required=True, default="RCUR", tracking=True)
    creditor_identifier = fields.Char(
        string="Creditor Identifier (ICS)", tracking=True,
        help="SEPA creditor identifier provided by your bank or national authority.")
    state = fields.Selection([
        ("draft", "Draft"),
        ("generated", "File Generated"),
        ("sent", "Sent to Bank"),
        ("rejected", "Rejected"),
        ("done", "Done"),
    ], string="Status", default="draft", tracking=True)
    line_ids = fields.One2many("sdd.batch.line", "batch_id", string="Collection Lines")
    nb_txs = fields.Integer(string="Transactions", compute="_compute_totals", store=True)
    ctrl_sum = fields.Monetary(
        string="Total Amount", compute="_compute_totals", currency_field="currency_id", store=True)
    msg_id = fields.Char(string="Message ID", copy=False, readonly=True)
    pmt_inf_id = fields.Char(string="Payment Info ID", copy=False, readonly=True)
    file_data = fields.Binary(string="pain.008 File", readonly=True, copy=False)
    file_name = fields.Char(string="File Name", readonly=True, copy=False)
    reject_reason = fields.Text(string="Rejection Details")
    note = fields.Text(string="Internal Notes")

    @api.depends("line_ids.amount")
    def _compute_totals(self):
        for batch in self:
            batch.nb_txs = len(batch.line_ids)
            batch.ctrl_sum = sum(batch.line_ids.mapped("amount"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("sdd.batch") or _("New")
        return super().create(vals_list)

    def _get_creditor_bank(self):
        self.ensure_one()
        bank = self.journal_id.bank_account_id
        if not bank:
            raise UserError(_("The bank journal must have a bank account configured."))
        iban = _clean_iban((bank.acc_number if "acc_number" in bank._fields else bank.account_number))
        if not _is_valid_iban(iban):
            raise UserError(_("The journal bank account IBAN is invalid: %s") % ((bank.acc_number if "acc_number" in bank._fields else bank.account_number) or ""))
        bic = (bank.bank_bic or "").strip().upper()
        return iban, bic

    def _prepare_tx_block(self, line):
        self.ensure_one()
        mandate = line.mandate_id
        partner = mandate.partner_id
        iban = _clean_iban(mandate.debtor_iban)
        if not _is_valid_iban(iban):
            raise UserError(_("Invalid IBAN for mandate %s.") % mandate.name)
        bic = (mandate.debtor_bic or "").strip().upper()
        bic_xml = "<BIC>%s</BIC>" % escape(bic) if bic else "<Othr><Id>NOTPROVIDED</Id></Othr>"
        end_to_end = escape((line.name or mandate.name)[:35])
        remittance = escape((line.communication or line.name or "")[:140])
        return f"""      <DrctDbtTxInf>
        <PmtId><EndToEndId>{end_to_end}</EndToEndId></PmtId>
        <InstdAmt Ccy="{escape(self.currency_id.name or 'EUR')}">{line.amount:.2f}</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>{escape((mandate.name or '')[:35])}</MndtId>
            <DtOfSgntr>{mandate.signature_date.isoformat()}</DtOfSgntr>
          </MndtRltdInf>
        </DrctDbtTx>
        <DbtrAgt><FinInstnId>{bic_xml}</FinInstnId></DbtrAgt>
        <Dbtr><Nm>{escape((partner.display_name or partner.name or '')[:70])}</Nm></Dbtr>
        <DbtrAcct><Id><IBAN>{iban}</IBAN></Id></DbtrAcct>
        <RmtInf><Ustrd>{remittance}</Ustrd></RmtInf>
      </DrctDbtTxInf>"""

    def _validate_for_generation(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Add at least one collection line before generating the file."))
        if not self.creditor_identifier:
            raise UserError(_("Set the SEPA creditor identifier (ICS) before generating the file."))
        for line in self.line_ids:
            mandate = line.mandate_id
            if mandate.state != "active":
                raise UserError(_("Mandate %s is not active.") % mandate.name)
            if mandate.scheme != self.scheme:
                raise UserError(_("Mandate %s uses scheme %s, but the batch uses %s.") % (
                    mandate.name, mandate.scheme, self.scheme))
            if line.amount <= 0:
                raise ValidationError(_("Collection line amounts must be positive."))

    def action_generate(self):
        for batch in self:
            batch._validate_for_generation()
            creditor_iban, creditor_bic = batch._get_creditor_bank()
            creditor_name = escape((batch.company_id.name or "Creditor")[:70])
            creditor_bic_xml = "<BIC>%s</BIC>" % escape(creditor_bic) if creditor_bic else "<Othr><Id>NOTPROVIDED</Id></Othr>"
            msg_id = (batch.msg_id or ("SDD-%s-%s" % (batch.name.replace("/", "-"), uuid.uuid4().hex[:8])))[:35]
            pmt_inf_id = (batch.pmt_inf_id or ("PMT-%s" % uuid.uuid4().hex[:10]))[:35]
            txs = "\n".join(batch._prepare_tx_block(line) for line in batch.line_ids)
            xml_content = PAIN008_TEMPLATE.format(
                msg_id=escape(msg_id),
                cre_dt_tm=fields.Datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                nb_txs=len(batch.line_ids),
                ctrl_sum=sum(batch.line_ids.mapped("amount")),
                creditor_name=creditor_name,
                creditor_iban=creditor_iban,
                creditor_bic_xml=creditor_bic_xml,
                creditor_id=escape((batch.creditor_identifier or "")[:35]),
                pmt_inf_id=escape(pmt_inf_id),
                reqd_date=batch.collection_date.isoformat(),
                scheme=batch.scheme,
                seq_tp=batch.sequence_type,
                txs=txs,
            )
            file_name = "pain008_%s_%s.xml" % (
                batch.name.replace("/", "-").replace(" ", "_"),
                batch.collection_date.isoformat(),
            )
            content = xml_content.encode("utf-8")
            try:
                from odoo.tools.binary import BinaryBytes as _BinVal
                file_data = _BinVal(content)
            except Exception:
                try:
                    from odoo.orm.fields_binary import BinaryBytes as _BinVal
                    file_data = _BinVal(content)
                except Exception:
                    file_data = base64.b64encode(content)
            batch.write({
                "msg_id": msg_id,
                "pmt_inf_id": pmt_inf_id,
                "file_data": file_data,
                "file_name": file_name,
                "state": "generated",
            })
            batch.line_ids.mapped("mandate_id").consume_sequence()
        return True

    def action_mark_sent(self):
        self.filtered(lambda b: b.state == "generated").write({"state": "sent"})

    def action_mark_done(self):
        self.filtered(lambda b: b.state in ("generated", "sent")).write({"state": "done"})

    def action_mark_rejected(self):
        self.filtered(lambda b: b.state in ("generated", "sent")).write({"state": "rejected"})

    def action_reset_to_draft(self):
        self.filtered(lambda b: b.state in ("rejected", "generated")).write({
            "state": "draft",
            "file_data": False,
            "file_name": False,
            "msg_id": False,
            "pmt_inf_id": False,
        })

    def action_download(self):
        self.ensure_one()
        if not self.file_data:
            raise UserError(_("No file has been generated yet."))
        attachment = self.env["ir.attachment"].create({
            "name": self.file_name or "pain008.xml",
            "datas": self.file_data,
            "type": "binary",
            "res_model": self._name,
            "res_id": self.id,
            "mimetype": "application/xml",
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }


class SddBatchLine(models.Model):
    _name = "sdd.batch.line"
    _description = "SEPA Direct Debit Batch Line"
    _order = "id"

    batch_id = fields.Many2one("sdd.batch", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="batch_id.company_id", store=True)
    currency_id = fields.Many2one(related="batch_id.currency_id", store=True)
    name = fields.Char(string="End-to-End Reference", required=True)
    mandate_id = fields.Many2one(
        "sdd.mandate", string="Mandate", required=True,
        domain="[('state', '=', 'active'), ('company_id', '=', company_id), ('scheme', '=', parent.scheme)]")
    partner_id = fields.Many2one(related="mandate_id.partner_id", string="Debtor", store=True, readonly=True)
    amount = fields.Monetary(string="Amount", required=True, currency_field="currency_id")
    communication = fields.Char(string="Remittance Information")
    invoice_id = fields.Many2one(
        "account.move", string="Related Invoice",
        domain="[('move_type', 'in', ('out_invoice', 'out_refund')), ('company_id', '=', company_id)]")

    @api.constrains("amount")
    def _check_amount(self):
        for line in self:
            if line.amount <= 0:
                raise ValidationError(_("The collection amount must be strictly positive."))

    @api.onchange("invoice_id")
    def _onchange_invoice_id(self):
        for line in self:
            if line.invoice_id:
                line.amount = abs(line.invoice_id.amount_residual or line.invoice_id.amount_total)
                line.communication = line.communication or line.invoice_id.payment_reference or line.invoice_id.name
                if line.invoice_id.partner_id and not line.mandate_id:
                    mandate = self.env["sdd.mandate"].search([
                        ("partner_id", "=", line.invoice_id.partner_id.id),
                        ("company_id", "=", line.company_id.id),
                        ("state", "=", "active"),
                        ("scheme", "=", line.batch_id.scheme),
                    ], limit=1)
                    line.mandate_id = mandate
                if not line.name:
                    line.name = line.invoice_id.name
