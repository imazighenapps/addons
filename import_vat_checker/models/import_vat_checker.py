# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ImportVatChecker(models.Model):
    _name = "import.vat.checker"
    _description = "Contrôle TVA import"
    _inherit = ["mail.thread"]
    _order = "period_end desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    period_start = fields.Date(string="Début période", required=True)
    period_end = fields.Date(string="Fin période", required=True)
    customs_vat_amount = fields.Monetary(string="TVA douane (pièces)", required=True, default=0.0)
    accounted_vat_amount = fields.Monetary(string="TVA import comptabilisée", compute="_compute_check", store=True)
    difference = fields.Monetary(string="Écart", compute="_compute_check", store=True)
    has_gap = fields.Boolean(string="Écart détecté", compute="_compute_check", store=True)
    justification = fields.Text(string="Justification des écarts")
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    state = fields.Selection([("draft","Brouillon"),("checked","Contrôlé"),("justified","Justifié")], default="draft", tracking=True)
    notes = fields.Text(string="Journal de conformité")

    @api.depends("period_start", "period_end", "company_id", "customs_vat_amount")
    def _compute_check(self):
        for rec in self:
            accounted = 0.0
            if rec.period_start and rec.period_end:
                moves = self.env["account.move"].search([
                    ("company_id","=",rec.company_id.id),("state","=","posted"),
                    ("date",">=",rec.period_start),("date","<=",rec.period_end),
                    ("move_type","in",["in_invoice","in_refund"])])
                # approximation: TVA sur factures fournisseurs de la période
                accounted = abs(sum(moves.mapped("amount_tax_signed")))
            rec.accounted_vat_amount = accounted
            rec.difference = (rec.customs_vat_amount or 0.0) - accounted
            rec.has_gap = abs(rec.difference) > 0.01

    def action_check(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("import.vat.checker") or "VATI"
            rec.state = "checked"
            rec.notes = (rec.notes or "") + ("\n[%s] Douane=%.2f Comptabilisé=%.2f Écart=%.2f" % (fields.Datetime.now(), rec.customs_vat_amount, rec.accounted_vat_amount, rec.difference))

    def action_justify(self):
        self.write({"state": "justified"})
