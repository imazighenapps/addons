# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VoucherAllocation(models.Model):
    _name = "voucher.allocation"
    _description = "Voucher Allocation"
    _inherit = ["mail.thread"]
    _order = "employee_id, id"

    period_id = fields.Many2one(
        "voucher.period", string="Period", required=True, ondelete="cascade", index=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, tracking=True)
    worked_days = fields.Integer(
        string="Worked Days", required=True, default=0, tracking=True)
    vouchers_earned = fields.Integer(
        string="Vouchers Earned", compute="_compute_vouchers", store=True)
    amount_value = fields.Monetary(
        string="Value", compute="_compute_vouchers", store=True,
        currency_field="currency_id")
    currency_id = fields.Many2one(
        related="period_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="period_id.company_id", store=True, readonly=True, index=True)
    note = fields.Char()

    @api.depends("worked_days", "period_id.voucher_value")
    def _compute_vouchers(self):
        for line in self:
            line.vouchers_earned = max(line.worked_days, 0)
            value = line.period_id.voucher_value or 0.0
            line.amount_value = line.vouchers_earned * value

    @api.constrains("worked_days", "period_id")
    def _check_worked_days(self):
        for line in self:
            if line.worked_days < 0:
                raise ValidationError(_(
                    "Worked days for %s cannot be negative.",
                    line.employee_id.name))
            if line.period_id and line.worked_days > line.period_id.working_days:
                raise ValidationError(_(
                    "Worked days for %s cannot exceed the working days of %s.",
                    line.employee_id.name, line.period_id.name))
