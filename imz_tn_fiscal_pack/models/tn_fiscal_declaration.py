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


class TnFiscalDeclaration(models.Model):
    _name = "tn.fiscal.declaration"
    _description = "Déclaration fiscale Tunisie"
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
    external_id = fields.Char(string="Identifiant externe", tracking=True)
    summary_note = fields.Text(string="Détails", readonly=True)
    status_note = fields.Text(string="Journal des statuts", readonly=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    vat_collected = fields.Monetary(string="TVA collectée", readonly=True)
    vat_deductible = fields.Monetary(string="TVA déductible", readonly=True)
    vat_due = fields.Monetary(string="TVA due", readonly=True)
    withholding_amount = fields.Monetary(string="Retenue à la source", readonly=True)
    tpae_status = fields.Selection([("pending","En attente"),("ready","Prêt TPAE"),("sent","Transmis")], string="Statut TPAE", default="pending")


    @api.constrains("period_start", "period_end")
    def _check_dates(self):
        for rec in self:
            if rec.period_start and rec.period_end and rec.period_start > rec.period_end:
                raise ValidationError(_("La date de début doit précéder la date de fin."))

    def action_generate(self):
        for rec in self:
            rec._ensure_name("tn.fiscal.decl")
            rec._compute_declaration()
            rec.state = "ready"
            rec._log(_("Déclaration générée."))

    def _compute_declaration(self):
        self.ensure_one()
        moves = self.env["account.move"].search([
            ("company_id", "=", self.company_id.id), ("state", "=", "posted"),
            ("date", ">=", self.period_start), ("date", "<=", self.period_end),
            ("move_type", "in", ["out_invoice","out_refund","in_invoice","in_refund"])])
        sales = moves.filtered(lambda m: m.move_type in ("out_invoice","out_refund"))
        purch = moves.filtered(lambda m: m.move_type in ("in_invoice","in_refund"))
        collected = abs(sum(sales.mapped("amount_tax_signed")))
        deductible = abs(sum(purch.mapped("amount_tax_signed")))
        due = max(collected - deductible, 0.0)
        vals = {"vat_collected": collected, "vat_deductible": deductible, "vat_due": due, "withholding_amount": 0.0, "tpae_status": "ready"}
        self.write(vals)
        payload = {"regime": "PCN/TVA", "period": [str(self.period_start), str(self.period_end)],
                   "vat_collected": collected, "vat_deductible": deductible, "vat_due": due, "tpae_status": "ready"}
        fname = "TN_FISCAL_%s_%s.json" % (self.period_start, self.period_end)
        summary = _("TVA collectée %.2f / déductible %.2f / due %.2f | TPAE prêt") % (collected, deductible, due)
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
