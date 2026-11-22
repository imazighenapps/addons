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


class UkMtdVatReturn(models.Model):
    _name = "uk.mtd.vat.return"
    _description = "MTD VAT Return (UK)"
    _inherit = ["mail.thread"]
    _order = "period_end desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    period_start = fields.Date(string="Début période", required=True)
    period_end = fields.Date(string="Fin période", required=True)
    invoice_id = fields.Many2one("account.move", string="Facture liée")
    state = fields.Selection(STATES, default="draft", tracking=True)
    file_name = fields.Char(string="Nom du fichier", readonly=True)
    file_data = fields.Binary(string="Fichier", readonly=True)
    generated_at = fields.Datetime(string="Généré le", readonly=True)
    external_id = fields.Char(string="Identifiant HMRC", tracking=True)
    summary_note = fields.Text(string="Détails", readonly=True)
    status_note = fields.Text(string="Journal des statuts", readonly=True)
    box1 = fields.Monetary(string="Box 1 VAT due sales", readonly=True)
    box2 = fields.Monetary(string="Box 2 VAT EC acquisitions", readonly=True)
    box3 = fields.Monetary(string="Box 3 Total VAT due", readonly=True)
    box4 = fields.Monetary(string="Box 4 VAT reclaimed", readonly=True)
    box5 = fields.Monetary(string="Box 5 Net VAT", readonly=True)
    box6 = fields.Monetary(string="Box 6 Total sales ex VAT", readonly=True)
    box7 = fields.Monetary(string="Box 7 Total purchases ex VAT", readonly=True)
    box8 = fields.Monetary(string="Box 8 Total EC supplies ex VAT", readonly=True)
    box9 = fields.Monetary(string="Box 9 Total EC acquisitions ex VAT", readonly=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)

    @api.constrains("period_start", "period_end")
    def _check_dates(self):
        for rec in self:
            if rec.period_start and rec.period_end and rec.period_start > rec.period_end:
                raise ValidationError(_("La date de début doit précéder la date de fin."))

    def action_generate(self):
        for rec in self:
            rec._ensure_name("uk.mtd.vat")
            rec._compute_boxes()
            rec.state = "ready"
            rec._log(_("VAT return 9 boxes calculée."))

    def _compute_boxes(self):
        self.ensure_one()
        domain = [("company_id", "=", self.company_id.id), ("state", "=", "posted"),
                  ("date", ">=", self.period_start), ("date", "<=", self.period_end),
                  ("move_type", "in", ["out_invoice", "out_refund", "in_invoice", "in_refund"])]
        moves = self.env["account.move"].search(domain)
        sales = moves.filtered(lambda m: m.move_type in ("out_invoice", "out_refund"))
        purchases = moves.filtered(lambda m: m.move_type in ("in_invoice", "in_refund"))
        sign_s = sum(m.amount_untaxed_signed for m in sales)
        tax_s = sum(m.amount_tax_signed for m in sales)
        sign_p = sum(-m.amount_untaxed_signed for m in purchases)
        tax_p = sum(-m.amount_tax_signed for m in purchases)
        box1 = abs(tax_s) if tax_s >= 0 else 0.0
        box4 = abs(tax_p) if tax_p >= 0 else 0.0
        vals = {
            "box1": box1, "box2": 0.0, "box3": box1, "box4": box4,
            "box5": abs(box1 - box4), "box6": abs(sign_s), "box7": abs(sign_p),
            "box8": 0.0, "box9": 0.0,
        }
        self.write(vals)
        payload = {
            "periodKey": self.period_end.strftime("%y%m") if self.period_end else "",
            "vatDueSales": vals["box1"], "vatDueAcquisitions": vals["box2"],
            "totalVatDue": vals["box3"], "vatReclaimedCurrPeriod": vals["box4"],
            "netVatDue": vals["box5"], "totalValueSalesExVAT": int(vals["box6"]),
            "totalValuePurchasesExVAT": int(vals["box7"]),
            "totalValueGoodsSuppliedExVAT": int(vals["box8"]),
            "totalValueAcquisitionsExVAT": int(vals["box9"]),
            "finalised": False,
        }
        fname = "MTD_VAT_%s_%s.json" % (self.period_start, self.period_end)
        summary = _("Box1=%.2f Box4=%.2f Box5=%.2f (Box6=%.0f Box7=%.0f)") % (
            vals["box1"], vals["box4"], vals["box5"], vals["box6"], vals["box7"])
        self._set_file(fname, json.dumps(payload, indent=2).encode("utf-8"), summary)

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
