# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LateFeeRule(models.Model):
    _name = "late.fee.rule"
    _description = "Late Fee Rule"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    annual_rate = fields.Float(
        string="Annual Rate (%)", required=True, default=10.0, tracking=True,
        help="Statutory annual interest rate applied to overdue amounts.")
    fixed_fee = fields.Monetary(
        string="Fixed Fee", default=0.0,
        help="Optional fixed recovery fee added to the interest.")
    line_ids = fields.One2many(
        "late.fee.line", "rule_id", string="Interest Lines")
    issued_amount = fields.Monetary(
        string="Issued Interest", compute="_compute_totals", store=True)
    line_count = fields.Integer(
        string="Lines", compute="_compute_totals", store=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("line_ids.interest_amount", "line_ids.state")
    def _compute_totals(self):
        for rule in self:
            issued = rule.line_ids.filtered(lambda l: l.state == "issued")
            rule.issued_amount = sum(issued.mapped("interest_amount"))
            rule.line_count = len(rule.line_ids)

    @api.constrains("annual_rate", "fixed_fee")
    def _check_rule(self):
        for rule in self:
            if rule.annual_rate < 0:
                raise ValidationError(_(
                    "The annual rate of %s cannot be negative.", rule.name))
            if rule.fixed_fee < 0:
                raise ValidationError(_(
                    "The fixed fee of %s cannot be negative.", rule.name))
