# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VoucherPeriod(models.Model):
    _name = "voucher.period"
    _description = "Voucher Period"
    _inherit = ["mail.thread"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    date_start = fields.Date(string="Period Start", required=True, tracking=True)
    date_end = fields.Date(string="Period End", required=True, tracking=True)
    working_days = fields.Integer(
        string="Working Days", required=True, default=20,
        help="Number of working days in the period used as the allocation ceiling.")
    voucher_value = fields.Monetary(
        string="Voucher Value", required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("validated", "Validated")],
        default="draft", required=True, tracking=True)
    line_ids = fields.One2many("voucher.allocation", "period_id", string="Allocations")
    total_vouchers = fields.Integer(
        string="Total Vouchers", compute="_compute_total", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True)
    note = fields.Text()

    @api.depends("line_ids.vouchers_earned")
    def _compute_total(self):
        for period in self:
            period.total_vouchers = sum(period.line_ids.mapped("vouchers_earned"))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for period in self:
            if period.date_end < period.date_start:
                raise ValidationError(_(
                    "The end date of %s cannot come before its start date.",
                    period.name))

    @api.constrains("working_days", "voucher_value")
    def _check_positive(self):
        for period in self:
            if period.working_days <= 0:
                raise ValidationError(_(
                    "The working days of %s must be above zero.", period.name))
            if period.voucher_value <= 0:
                raise ValidationError(_(
                    "The voucher value of %s must be above zero.", period.name))

    def action_validate(self):
        for period in self:
            if period.state != "draft":
                raise ValidationError(_(
                    "Only a draft period can be validated."))
            period.state = "validated"
        return True

    def action_reset_draft(self):
        for period in self:
            if period.state != "validated":
                raise ValidationError(_(
                    "Only a validated period can be reset to draft."))
            period.state = "draft"
        return True
