# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class IntercompanyLoan(models.Model):
    _name = "intercompany.loan"
    _description = "Prêt intersociétés"
    _inherit = ["mail.thread"]
    _order = "start_date desc, id desc"

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", string="Prêteur", required=True, default=lambda self: self.env.company)
    borrower_company_id = fields.Many2one("res.company", string="Emprunteur", required=True)
    principal_amount = fields.Monetary(string="Capital", required=True)
    interest_rate = fields.Float(string="Taux annuel (%)", required=True, default=3.0)
    term_months = fields.Integer(string="Durée (mois)", required=True, default=12)
    start_date = fields.Date(string="Date de début", default=fields.Date.context_today, required=True)
    maturity_date = fields.Date(string="Échéance", compute="_compute_schedule", store=True)
    monthly_payment = fields.Monetary(string="Mensualité (capital)", compute="_compute_schedule", store=True)
    total_interest = fields.Monetary(string="Intérêts totaux estimés", compute="_compute_schedule", store=True)
    outstanding_amount = fields.Monetary(string="Capital restant dû", compute="_compute_schedule", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    state = fields.Selection([("draft","Brouillon"),("running","En cours"),("closed","Soldé"),("cancelled","Annulé")], default="draft", tracking=True)
    notes = fields.Text(string="Notes / convention")

    @api.depends("principal_amount", "interest_rate", "term_months", "start_date")
    def _compute_schedule(self):
        for rec in self:
            if rec.start_date and rec.term_months:
                rec.maturity_date = rec.start_date + relativedelta(months=+rec.term_months)
            else:
                rec.maturity_date = False
            months = rec.term_months or 1
            rec.monthly_payment = (rec.principal_amount or 0.0) / months if months else 0.0
            rec.total_interest = (rec.principal_amount or 0.0) * (rec.interest_rate or 0.0) / 100.0 * (months / 12.0)
            rec.outstanding_amount = rec.principal_amount or 0.0

    @api.constrains("company_id", "borrower_company_id")
    def _check_companies(self):
        for rec in self:
            if rec.company_id == rec.borrower_company_id:
                raise UserError(_("Le prêteur et l'emprunteur doivent être différents."))

    @api.constrains("principal_amount", "term_months")
    def _check_positive(self):
        for rec in self:
            if rec.principal_amount <= 0 or rec.term_months <= 0:
                raise ValidationError(_("Le capital et la durée doivent être positifs."))

    def action_start(self):
        for rec in self:
            if not rec.name or rec.name == "Nouveau":
                rec.name = self.env["ir.sequence"].next_by_code("intercompany.loan") or "ICL"
            rec.state = "running"

    def action_close(self):
        self.write({"state": "closed", "outstanding_amount": 0.0})
    def action_cancel(self):
        self.write({"state": "cancelled"})
