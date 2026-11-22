# -*- coding: utf-8 -*-
import base64
import hashlib
from datetime import date

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

STATES = [
    ("draft", "Brouillon"), ("ready", "Prête"), ("sent", "Envoyée"),
    ("accepted", "Acceptée"), ("rejected", "Refusée"),
]


class ChQrbillDocument(models.Model):
    _name = "ch.qrbill.document"
    _description = "QR-bill Suisse"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    invoice_id = fields.Many2one(
        "account.move", string="Facture", required=True,
        domain="[('move_type','in',['out_invoice','out_refund']),('company_id','=',company_id),('state','=','posted')]")
    partner_id = fields.Many2one(related="invoice_id.partner_id", store=True)
    state = fields.Selection(STATES, default="draft", tracking=True)
    file_name = fields.Char(readonly=True)
    file_data = fields.Binary(string="Fichier", readonly=True)
    generated_at = fields.Datetime(readonly=True)
    external_id = fields.Char(string="Identifiant externe", tracking=True)
    status_note = fields.Text(string="Journal des statuts", readonly=True)

    creditor_reference = fields.Char(string="Référence créancier")
    qr_payload = fields.Text(string="Payload QR-bill", readonly=True)

    _sql_constraints = [("ch_qrbill_document_invoice_uniq", "unique(invoice_id)", "Document déjà existant pour cette facture.")]

    def action_generate(self):
        for rec in self:
            if not rec.name or rec.name == _("Nouveau"):
                rec.name = self.env["ir.sequence"].next_by_code("ch.qrbill.document") or "QRB"
            rec._generate_payload()
            rec.state = "ready"
            rec._log(_("QR-bill généré."))

    def _generate_payload(self):
        self.ensure_one()
        inv = self.invoice_id
        company = self.company_id
        iban = ""
        if company.partner_id.bank_ids:
            iban = (company.partner_id.bank_ids[0].acc_number or "").replace(" ", "")
        ref = self.creditor_reference or inv.payment_reference or inv.name or ""
        lines = [
            "SPC", "0200", "1",
            iban or "CH0000000000000000000",
            "S", company.name or "", company.street or "",
            (company.zip or "") + " " + (company.city or ""), "", "", company.country_id.code or "CH",
            "", "", "", "", "", "", "",
            "%.2f" % (inv.amount_residual or inv.amount_total or 0.0),
            inv.currency_id.name or "CHF",
            "S", inv.partner_id.name or "", inv.partner_id.street or "",
            (inv.partner_id.zip or "") + " " + (inv.partner_id.city or ""), "", "", inv.partner_id.country_id.code or "CH",
            "SCOR", ref, "", "EPD", "",
        ]
        payload = "\n".join(lines)
        fname = "QRBill_%s.txt" % (inv.name or "INV").replace("/", "_")
        self.write({
            "file_name": fname,
            "file_data": base64.b64encode(payload.encode("utf-8")).decode("ascii"),
            "generated_at": fields.Datetime.now(),
            "qr_payload": payload,
        })

    def action_mark_sent(self):
        self.write({"state": "sent"})
        self._log(_("Marquée envoyée."))

    def action_mark_accepted(self):
        self.write({"state": "accepted"})
        self._log(_("Acceptée."))

    def action_mark_rejected(self):
        self.write({"state": "rejected"})
        self._log(_("Refusée."))

    def _log(self, msg):
        now = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for rec in self:
            prev = rec.status_note or ""
            rec.status_note = ("[%s] %s\n%s" % (now, msg, prev)).strip()
