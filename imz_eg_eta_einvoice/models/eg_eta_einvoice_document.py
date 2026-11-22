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


class EgEtaDocument(models.Model):
    _name = "eg.eta.einvoice.document"
    _description = "e-Invoice ETA Égypte"
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
    external_id = fields.Char(string="Submission ID ETA", tracking=True)
    summary_note = fields.Text(string="Détails", readonly=True)
    status_note = fields.Text(string="Journal des statuts", readonly=True)
    rejection_reason = fields.Text(string="Motif de rejet")

    _sql_constraints = [("eg_eta_einvoice_document_invoice_uniq", "unique(invoice_id)", "Document déjà existant pour cette facture.")]

    def action_generate(self):
        for rec in self:
            rec._ensure_name("eg.eta.einvoice")
            rec._generate()
            rec.state = "ready"
            rec._log(_("Document ETA JSON généré."))

    def _generate(self):
        self.ensure_one()
        inv = self.invoice_id
        sub_id = hashlib.sha1(((inv.name or "") + str(inv.id)).encode()).hexdigest()[:20]
        doc = {
            "issuer": {"name": self.company_id.name or "", "id": self.company_id.vat or "", "type": "B"},
            "receiver": {"name": inv.partner_id.name or "", "id": inv.partner_id.vat or "", "type": "B"},
            "documentType": "I",
            "documentTypeVersion": "1.0",
            "dateTimeIssued": (inv.invoice_date or date.today()).strftime("%Y-%m-%dT00:00:00Z"),
            "internalID": inv.name or "",
            "invoiceLines": [{"description": l.name or "", "itemType": "GS1", "itemCode": "10000000",
                               "quantity": l.quantity, "unitValue": {"amountEGP": l.price_unit},
                               "salesTotal": l.price_subtotal, "total": l.price_total}
                              for l in inv.invoice_line_ids],
            "totalSalesAmount": inv.amount_untaxed,
            "totalAmount": inv.amount_total,
            "extraDiscountAmount": 0.0,
            "netAmount": inv.amount_total,
        }
        fname = "ETA_%s.json" % (inv.name or "INV").replace("/", "_")
        self.write({"external_id": sub_id})
        summary = _("Submission: %s | Total: %.2f") % (sub_id, inv.amount_total or 0.0)
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
