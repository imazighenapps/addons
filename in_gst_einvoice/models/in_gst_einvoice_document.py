# -*- coding: utf-8 -*-
import base64
import hashlib
import json
from datetime import date

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

STATES = [
    ("draft", "Brouillon"), ("ready", "Prête"), ("sent", "Envoyée"),
    ("accepted", "Acceptée"), ("rejected", "Refusée"),
]


class InGstEinvoiceDocument(models.Model):
    _name = "in.gst.einvoice.document"
    _description = "GST e-Invoice Inde (IRN)"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    period_start = fields.Date(string="Début période")
    period_end = fields.Date(string="Fin période")
    invoice_id = fields.Many2one("account.move", string="Facture liée", required=True,
        domain="[('move_type','in',['out_invoice','out_refund']),('company_id','=',company_id),('state','=','posted')]")
    state = fields.Selection(STATES, default="draft", tracking=True)
    file_name = fields.Char(string="Nom du fichier", readonly=True)
    file_data = fields.Binary(string="Fichier", readonly=True)
    generated_at = fields.Datetime(string="Généré le", readonly=True)
    external_id = fields.Char(string="IRN", tracking=True)
    summary_note = fields.Text(string="Détails", readonly=True)
    status_note = fields.Text(string="Journal des statuts", readonly=True)
    ack_no = fields.Char(string="Ack No", readonly=True)
    signed_qr = fields.Text(string="Signed QR", readonly=True)

    _sql_constraints = [("in_gst_einvoice_document_invoice_uniq", "unique(invoice_id)", "Document déjà existant pour cette facture.")]

    def action_generate(self):
        for rec in self:
            rec._ensure_name("in.gst.einvoice")
            rec._generate()
            rec.state = "ready"
            rec._log(_("JSON GST / IRN généré."))

    def _generate(self):
        self.ensure_one()
        inv = self.invoice_id
        irn = hashlib.sha256(((self.company_id.vat or "") + (inv.name or "")).encode()).hexdigest()
        doc = {
            "Version": "1.1",
            "TranDtls": {"TaxSch": "GST", "SupTyp": "B2B", "RegRev": "N"},
            "DocDtls": {"Typ": "INV" if inv.move_type == "out_invoice" else "CRN",
                        "No": inv.name or "", "Dt": (inv.invoice_date or date.today()).strftime("%d/%m/%Y")},
            "SellerDtls": {"Gstin": self.company_id.vat or "", "LglNm": self.company_id.name or ""},
            "BuyerDtls": {"Gstin": inv.partner_id.vat or "URP", "LglNm": inv.partner_id.name or ""},
            "ItemList": [{"SlNo": str(i+1), "PrdDesc": (l.name or "")[:50], "Qty": l.quantity,
                          "UnitPrice": l.price_unit, "TotAmt": l.price_subtotal}
                         for i, l in enumerate(inv.invoice_line_ids)],
            "ValDtls": {"AssVal": inv.amount_untaxed, "IgstVal": inv.amount_tax, "TotInvVal": inv.amount_total},
            "Irn": irn,
        }
        ack = "ACK%s" % (abs(hash(irn)) % 10**9)
        self.write({"external_id": irn, "ack_no": ack, "signed_qr": irn[:64]})
        fname = "GST_IRN_%s.json" % (inv.name or "INV").replace("/", "_")
        summary = _("IRN: %s… | Ack: %s | Total: %.2f") % (irn[:16], ack, inv.amount_total or 0.0)
        self._set_file(fname, json.dumps(doc, indent=2).encode("utf-8"), summary)

    def action_mark_sent(self):
        for rec in self:
            if rec.state not in ("ready", "rejected"):
                raise UserError(_("Le document doit être prêt ou refusé pour être envoyé."))
            rec._log(_("Marqué comme envoyé."))
            rec.state = "sent"

    def action_mark_accepted(self):
        self.write({"state": "accepted"})
        self._log(_("Acceptée."))

    def action_mark_rejected(self):
        self.write({"state": "rejected"})
        self._log(_("Refusée."))

    def action_reset(self):
        self.write({"state": "draft", "file_data": False, "file_name": False})

    def _log(self, msg):
        now = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for rec in self:
            prev = rec.status_note or ""
            rec.status_note = ("[%s] %s\n%s" % (now, msg, prev)).strip()

    def _ensure_name(self, code):
        for rec in self:
            if not rec.name or rec.name in (_("Nouveau"), "Nouveau"):
                rec.name = self.env["ir.sequence"].next_by_code(code) or rec.name

    def _set_file(self, fname, content_bytes, summary=""):
        self.write({
            "file_name": fname,
            "file_data": base64.b64encode(content_bytes).decode("ascii"),
            "generated_at": fields.Datetime.now(),
            "summary_note": summary,
        })
