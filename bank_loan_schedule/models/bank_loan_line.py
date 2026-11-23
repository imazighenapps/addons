# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class BankLoanLine(models.Model):
    _name = "bank.loan.line"
    _description = "Échéance d'emprunt"
    _order = "sequence asc"

    loan_id = fields.Many2one("bank.loan", required=True, ondelete="cascade")
    sequence = fields.Integer(string="#")
    due_date = fields.Date(string="Échéance", required=True)
    capital_amount = fields.Monetary(string="Capital")
    interest_amount = fields.Monetary(string="Intérêts")
    insurance_amount = fields.Monetary(string="Assurance")
    total_amount = fields.Monetary(string="Total échéance", compute="_compute_total", store=True)
    currency_id = fields.Many2one(related="loan_id.currency_id", readonly=True)
    state = fields.Selection([("due","À payer"),("paid","Payée")], default="due")

    @api.depends("capital_amount", "interest_amount", "insurance_amount")
    def _compute_total(self):
        for rec in self:
            rec.total_amount = (rec.capital_amount or 0.0) + (rec.interest_amount or 0.0) + (rec.insurance_amount or 0.0)
