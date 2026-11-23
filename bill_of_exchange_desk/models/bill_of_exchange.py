# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BillOfExchange(models.Model):
    _name = "bill.of.exchange"
    _description = "Effet de commerce (LCR)"
    _inherit = ["mail.thread"]
    _order = "due_date asc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    invoice_id = fields.Many2one("account.move", string="Facture source", required=True,
        domain="[('move_type','=','out_invoice'),('company_id','=',company_id),('state','=','posted')]")
    partner_id = fields.Many2one(related="invoice_id.partner_id", store=True)
    amount = fields.Monetary(string="Montant", required=True)
    currency_id = fields.Many2one(related="invoice_id.currency_id", store=True, readonly=True)
    issue_date = fields.Date(string="Date d'émission", default=fields.Date.context_today)
    due_date = fields.Date(string="Échéance", required=True)
    # bank_id = fields.Many2one("res.bank", string="Banque de domiciliation")
    bank_name = fields.Char(string="Banque de domiciliation")
    discount_rate = fields.Float(string="Taux d'escompte (%)")
    discount_amount = fields.Monetary(string="Intérêts d'escompte", compute="_compute_discount", store=True)
    net_amount = fields.Monetary(string="Net escompté", compute="_compute_discount", store=True)
    state = fields.Selection([
        ("draft","Brouillon"),("portfolio","En portefeuille"),("domiciled","Domicilié"),
        ("discounted","Escompté"),("paid","Encaissé"),("rejected","Rejeté")
    ], default="draft", tracking=True)
    rejection_reason = fields.Text(string="Motif de rejet")
    notes = fields.Text(string="Notes")

    @api.depends("amount", "discount_rate")
    def _compute_discount(self):
        for rec in self:
            rec.discount_amount = rec.amount * (rec.discount_rate or 0.0) / 100.0
            rec.net_amount = rec.amount - rec.discount_amount

    @api.onchange("invoice_id")
    def _onchange_invoice(self):
        if self.invoice_id:
            self.amount = self.invoice_id.amount_residual or self.invoice_id.amount_total

    def action_portfolio(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("bill.of.exchange") or "LCR"
            rec.state = "portfolio"

    def action_domicile(self):
        self.write({"state": "domiciled"})
    def action_discount(self):
        self.write({"state": "discounted"})
    def action_paid(self):
        self.write({"state": "paid"})
    def action_reject(self):
        self.write({"state": "rejected"})
