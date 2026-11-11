# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AdvanceRepayment(models.Model):
    _name = "advance.repayment"
    _description = "Advance Repayment"
    _inherit = ["mail.thread"]
    _order = "due_date, id"

    request_id = fields.Many2one(
        "advance.request", string="Advance", required=True, ondelete="cascade", index=True)
    employee_id = fields.Many2one(
        related="request_id.employee_id", store=True, string="Employee")
    due_date = fields.Date(string="Due Date", required=True, tracking=True)
    amount = fields.Monetary(string="Amount", required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        related="request_id.currency_id", store=True, readonly=True)
    state = fields.Selection(
        [("planned", "Planned"), ("paid", "Paid")],
        default="planned", required=True, tracking=True)
    paid_date = fields.Date(string="Paid Date", readonly=True, copy=False)
    company_id = fields.Many2one(
        related="request_id.company_id", store=True, readonly=True, index=True)
    note = fields.Char()

    @api.constrains("amount")
    def _check_amount(self):
        for line in self:
            if line.amount <= 0:
                raise ValidationError(_(
                    "The repayment amount for %s must be above zero.",
                    line.request_id.name))

    @api.constrains("amount", "request_id")
    def _check_request_total(self):
        for line in self:
            request = line.request_id
            if not request:
                continue
            total = sum(request.line_ids.mapped("amount"))
            if total - request.amount > 0.00001:
                raise ValidationError(_(
                    "The repayment schedule of %s exceeds the approved amount.",
                    request.name))

    def action_mark_paid(self):
        for line in self:
            if line.state != "planned":
                raise ValidationError(_(
                    "Only a planned repayment can be marked as paid."))
            line.write({
                "state": "paid",
                "paid_date": fields.Date.context_today(line),
            })
        return True
