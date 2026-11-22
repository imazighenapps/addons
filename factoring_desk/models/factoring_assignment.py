# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FactoringAssignment(models.Model):
    _name = "factoring.assignment"
    _description = "Cession d'affacturage"
    _inherit = ["mail.thread"]
    _order = "cession_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    factor_name = fields.Char(string="Factor", required=True)
    invoice_id = fields.Many2one("account.move", string="Facture cédée", required=True,
        domain="[('move_type','=','out_invoice'),('company_id','=',company_id),('state','=','posted')]")
    partner_id = fields.Many2one(related="invoice_id.partner_id", store=True)
    cession_date = fields.Date(string="Date de cession", default=fields.Date.context_today)
    invoice_amount = fields.Monetary(string="Montant facture", related="invoice_id.amount_total", store=True)
    advance_rate = fields.Float(string="Taux d'avance (%)", default=80.0)
    commission_rate = fields.Float(string="Commission (%)", default=1.5)
    retention_rate = fields.Float(string="Retenue de garantie (%)", default=10.0)
    advance_amount = fields.Monetary(string="Avance", compute="_compute_amounts", store=True)
    commission_amount = fields.Monetary(string="Commission", compute="_compute_amounts", store=True)
    retention_amount = fields.Monetary(string="Retenue", compute="_compute_amounts", store=True)
    released_amount = fields.Monetary(string="Montant débloqué", readonly=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    state = fields.Selection([
        ("draft","Brouillon"),("assigned","Cédée"),("advanced","Avance versée"),("released","Débloquée"),("closed","Clôturée")
    ], default="draft", tracking=True)
    notes = fields.Text(string="Notes")

    @api.depends("invoice_amount", "advance_rate", "commission_rate", "retention_rate")
    def _compute_amounts(self):
        for rec in self:
            base = rec.invoice_amount or 0.0
            rec.advance_amount = base * (rec.advance_rate or 0.0) / 100.0
            rec.commission_amount = base * (rec.commission_rate or 0.0) / 100.0
            rec.retention_amount = base * (rec.retention_rate or 0.0) / 100.0

    def action_assign(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("factoring.assignment") or "FACT"
            rec.state = "assigned"

    def action_advance(self):
        self.write({"state": "advanced"})

    def action_release(self):
        for rec in self:
            rec.released_amount = max((rec.invoice_amount or 0.0) - rec.commission_amount - rec.advance_amount, rec.retention_amount)
            rec.state = "released"

    def action_close(self):
        self.write({"state": "closed"})
