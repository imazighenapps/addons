# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FeeContract(models.Model):
    _name = "fee.contract"
    _description = "Payment Fee Contract"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    provider = fields.Char(
        required=True, tracking=True,
        help="Name of the payment platform that bills the fees.")
    rate_percent = fields.Float(
        string="Rate (%)", required=True, default=0.0, tracking=True,
        help="Percentage of the settled amount charged per transaction.")
    fixed_fee = fields.Monetary(
        string="Fixed Fee", currency_field="currency_id", default=0.0,
        help="Fixed amount charged on every transaction.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many(
        "fee.line", "contract_id", string="Billed Fees")
    line_count = fields.Integer(
        string="Fee Lines", compute="_compute_line_stats", store=True)
    variance_line_count = fields.Integer(
        string="Variance Lines", compute="_compute_line_stats", store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.variance_amount")
    def _compute_line_stats(self):
        for contract in self:
            lines = contract.line_ids
            contract.line_count = len(lines)
            contract.variance_line_count = len(lines.filtered(
                lambda line: abs(line.variance_amount) > 0.00001))

    @api.constrains("rate_percent", "fixed_fee")
    def _check_rates(self):
        for contract in self:
            if contract.rate_percent < 0.0:
                raise ValidationError(_(
                    "The rate of contract %s cannot be negative.",
                    contract.name))
            if contract.fixed_fee < 0.0:
                raise ValidationError(_(
                    "The fixed fee of contract %s cannot be negative.",
                    contract.name))
