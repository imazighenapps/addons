# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RebateContract(models.Model):
    _name = "rebate.contract"
    _description = "Rebate Contract"
    _inherit = ["mail.thread"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True,
        index=True)
    date_start = fields.Date(required=True, default=fields.Date.context_today,
                             tracking=True)
    date_end = fields.Date(required=True, tracking=True)
    rate = fields.Float(
        string="Rebate Rate (%)", required=True, default=2.0,
        help="Percentage of eligible turnover accrued as rebate.")
    target_amount = fields.Monetary(
        string="Target Turnover", currency_field="currency_id",
        help="Turnover level the rebate agreement is based on.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    accrual_ids = fields.One2many(
        "rebate.accrual", "contract_id", string="Accruals")
    accrued_amount = fields.Monetary(
        string="Accrued", currency_field="currency_id",
        compute="_compute_amounts", store=True,
        help="Total amount accrued on this contract.")
    settled_amount = fields.Monetary(
        string="Settled", currency_field="currency_id",
        compute="_compute_amounts", store=True,
        help="Amount already paid out to the customer.")
    remaining_amount = fields.Monetary(
        string="Remaining", currency_field="currency_id",
        compute="_compute_amounts", store=True,
        help="Accrued amount still to settle.")
    accrual_count = fields.Integer(
        string="Accruals", compute="_compute_amounts", store=True)
    state = fields.Selection(
        [("open", "Open"), ("settled", "Settled")],
        default="open", required=True, tracking=True, index=True)
    settled_on = fields.Date(string="Settled On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("accrual_ids.amount", "accrual_ids.state", "state")
    def _compute_amounts(self):
        for contract in self:
            lines = contract.accrual_ids
            contract.accrued_amount = sum(lines.mapped("amount"))
            settled = sum(lines.filtered(
                lambda line: line.state == "settled").mapped("amount"))
            if contract.state == "settled":
                settled = contract.accrued_amount
            contract.settled_amount = settled
            contract.remaining_amount = contract.accrued_amount - settled
            contract.accrual_count = len(lines)

    @api.constrains("rate")
    def _check_rate(self):
        for contract in self:
            if contract.rate <= 0 or contract.rate > 100:
                raise ValidationError(_(
                    "The rebate rate of %s must be between 0 and 100.",
                    contract.name))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for contract in self:
            if contract.date_end < contract.date_start:
                raise ValidationError(_(
                    "The end date of %s cannot come before the start date.",
                    contract.name))

    @api.constrains("target_amount")
    def _check_target_amount(self):
        for contract in self:
            if contract.target_amount < 0:
                raise ValidationError(_(
                    "The target turnover of %s cannot be negative.",
                    contract.name))

    def action_settle(self):
        for contract in self:
            if contract.state != "open":
                raise ValidationError(_(
                    "The rebate contract %s is already settled.", contract.name))
            contract.write({
                "state": "settled",
                "settled_on": fields.Date.context_today(contract),
            })
            contract.accrual_ids.filtered(
                lambda line: line.state == "open").write({"state": "settled"})
            contract.message_post(body=_(
                "The rebate contract has been settled for %s.",
                contract.accrued_amount))
        return True
