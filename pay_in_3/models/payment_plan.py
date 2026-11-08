# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PaymentPlan(models.Model):
    _name = "payment.plan"
    _description = "Payment Plan"
    _inherit = ["mail.thread"]
    _order = "first_due_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    move_id = fields.Many2one(
        "account.move", string="Invoice", required=True,
        ondelete="cascade", domain=[("move_type", "=", "out_invoice")])
    partner_id = fields.Many2one(
        related="move_id.partner_id", store=True, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="move_id.currency_id", store=True, readonly=True)
    total_amount = fields.Monetary(
        string="Total", currency_field="currency_id", required=True)
    installment_count = fields.Integer(
        string="Installments", default=3, required=True)
    first_due_date = fields.Date(required=True)
    interval_days = fields.Integer(string="Interval (days)", default=30)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("done", "Done"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    line_ids = fields.One2many(
        "payment.plan.line", "plan_id", string="Installments")
    paid_amount = fields.Monetary(
        string="Paid", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    remaining_amount = fields.Monetary(
        string="Remaining", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    note = fields.Text()

    @api.depends("move_id")
    def _compute_name(self):
        for plan in self:
            plan.name = "%s / Plan" % (plan.move_id.name or "") \
                if plan.move_id else _("Payment Plan")

    @api.depends("line_ids.paid_amount", "total_amount")
    def _compute_amounts(self):
        for plan in self:
            plan.paid_amount = sum(plan.line_ids.mapped("paid_amount"))
            plan.remaining_amount = (plan.total_amount or 0.0) \
                - plan.paid_amount

    def _generate_lines(self):
        self.ensure_one()
        self.line_ids.unlink()
        count = max(self.installment_count or 1, 1)
        currency = self.currency_id or self.company_id.currency_id
        total = currency.round(self.total_amount or 0.0)
        share = currency.round(total / count)
        Line = self.env["payment.plan.line"]
        for index in range(count):
            amount = total - share * (count - 1) if index == count - 1 \
                else share
            Line.create({
                "plan_id": self.id,
                "sequence": (index + 1) * 10,
                "due_date": self.first_due_date
                + timedelta(days=(self.interval_days or 0) * index),
                "amount": amount,
            })

    def action_confirm(self):
        for plan in self:
            if not plan.line_ids:
                plan._generate_lines()
            plan.state = "active"
        return True

    def action_cancel(self):
        for plan in self:
            plan.state = "cancelled"
        return True

    def action_recompute(self):
        for plan in self:
            if plan.line_ids.filtered(lambda l: l.paid_amount):
                raise UserError(_(
                    "An installment is already paid: the plan cannot be "
                    "recomputed."))
            plan._generate_lines()
        return True
