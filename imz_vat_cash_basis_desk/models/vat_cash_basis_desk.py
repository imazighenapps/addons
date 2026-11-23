# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class VatCashBasis(models.Model):
    _name = "vat.cash.basis.desk"
    _description = "TVA sur encaissements"
    _inherit = ["mail.thread"]
    _order = "period_end desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    period_start = fields.Date(string="Début période", required=True)
    period_end = fields.Date(string="Fin période", required=True)
    collected_vat_due = fields.Monetary(string="TVA due (encaissée)", compute="_compute_vat", store=True)
    collected_vat_deductible = fields.Monetary(string="TVA déductible (décaissée)", compute="_compute_vat", store=True)
    net_vat = fields.Monetary(string="TVA nette", compute="_compute_vat", store=True)
    unpaid_regularization = fields.Monetary(string="Régularisation impayés")
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    state = fields.Selection([("draft","Brouillon"),("computed","Calculé"),("validated","Validé")], default="draft", tracking=True)
    notes = fields.Text(string="Notes / conformité")

    @api.depends("period_start", "period_end", "company_id", "unpaid_regularization")
    def _compute_vat(self):
        for rec in self:
            domain = [("company_id","=",rec.company_id.id),("state","=","posted"),("date",">=",rec.period_start),("date","<=",rec.period_end)]
            moves = self.env["account.move"].search(domain + [("move_type","in",["out_invoice","out_refund","in_invoice","in_refund"])]) if rec.period_start and rec.period_end else self.env["account.move"]
            out = moves.filtered(lambda m: m.move_type in ("out_invoice","out_refund"))
            inp = moves.filtered(lambda m: m.move_type in ("in_invoice","in_refund"))
            rec.collected_vat_due = abs(sum(out.mapped("amount_tax_signed")))
            rec.collected_vat_deductible = abs(sum(inp.mapped("amount_tax_signed")))
            rec.net_vat = rec.collected_vat_due - rec.collected_vat_deductible - (rec.unpaid_regularization or 0.0)

    def action_compute(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("vat.cash.basis.desk") or "VATC"
            rec.state = "computed"

    def action_validate(self):
        self.write({"state": "validated"})
