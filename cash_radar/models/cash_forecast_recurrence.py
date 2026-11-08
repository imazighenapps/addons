# -*- coding: utf-8 -*-
from odoo import fields, models


class CashForecastRecurrence(models.Model):
    _name = "cash.forecast.recurrence"
    _description = "Recurring Cash Entry"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    amount = fields.Monetary(
        string="Amount", currency_field="currency_id", required=True,
        help="Positive is an inflow, negative an outflow.")
    frequency = fields.Selection(
        [("weekly", "Weekly"), ("monthly", "Monthly"),
         ("quarterly", "Quarterly")],
        default="monthly", required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date()
    partner_id = fields.Many2one("res.partner", string="Partner")
    category = fields.Selection(
        [("sales", "Sales"), ("purchase", "Purchase"),
         ("payroll", "Payroll"), ("tax", "Tax"), ("other", "Other")],
        default="other", required=True)
    active = fields.Boolean(default=True)
    note = fields.Text()
