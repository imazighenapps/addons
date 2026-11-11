# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AdvanceRequest(models.Model):
    _name = "advance.request"
    _description = "Salary Advance Request"
    _inherit = ["mail.thread"]
    _order = "request_date desc, id desc"

    name = fields.Char(
        required=True, default=lambda self: _("Advance %s") % fields.Date.context_today(self),
        tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, tracking=True, index=True)
    amount = fields.Monetary(
        string="Advance Amount", required=True, tracking=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    request_date = fields.Date(
        string="Request Date", required=True, default=fields.Date.context_today, tracking=True)
    approval_date = fields.Date(string="Approval Date", tracking=True)
    reason = fields.Text(help="Why the employee requested the advance.")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("refused", "Refused"), ("repaid", "Repaid")],
        default="draft", required=True, tracking=True, index=True)
    line_ids = fields.One2many("advance.repayment", "request_id", string="Repayments")
    repaid_amount = fields.Monetary(
        string="Repaid Amount", compute="_compute_balance", store=True,
        currency_field="currency_id")
    remaining_amount = fields.Monetary(
        string="Remaining Amount", compute="_compute_balance", store=True,
        currency_field="currency_id")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True)
    note = fields.Text()

    @api.depends("amount", "line_ids.amount", "line_ids.state")
    def _compute_balance(self):
        for request in self:
            repaid = sum(request.line_ids.filtered(
                lambda line: line.state == "paid").mapped("amount"))
            request.repaid_amount = repaid
            request.remaining_amount = request.amount - repaid

    @api.constrains("amount")
    def _check_amount(self):
        for request in self:
            if request.amount <= 0:
                raise ValidationError(_(
                    "The advance amount for %s must be above zero.",
                    request.employee_id.name))

    @api.constrains("line_ids", "amount")
    def _check_schedule_total(self):
        for request in self:
            total = sum(request.line_ids.mapped("amount"))
            if total - request.amount > 0.00001:
                raise ValidationError(_(
                    "The repayment schedule of %s exceeds the approved amount.",
                    request.name))

    def action_submit(self):
        for request in self:
            if request.state != "draft":
                raise ValidationError(_(
                    "Only a draft advance can be submitted."))
            request.state = "submitted"
        return True

    def action_approve(self):
        for request in self:
            if request.state != "submitted":
                raise ValidationError(_(
                    "Only a submitted advance can be approved."))
            request.write({
                "state": "approved",
                "approval_date": fields.Date.context_today(request),
            })
        return True

    def action_refuse(self):
        for request in self:
            if request.state not in ("draft", "submitted"):
                raise ValidationError(_(
                    "Only a draft or submitted advance can be refused."))
            request.state = "refused"
        return True

    def action_close(self):
        for request in self:
            if request.state != "approved":
                raise ValidationError(_(
                    "Only an approved advance can be closed."))
            if request.remaining_amount > 0.00001:
                raise ValidationError(_(
                    "The advance %s still has an unpaid balance.", request.name))
            request.state = "repaid"
        return True
