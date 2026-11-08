# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PaymentPlanLine(models.Model):
    _name = "payment.plan.line"
    _description = "Payment Plan Installment"
    _order = "sequence, id"

    name = fields.Char(compute="_compute_name", store=True)
    plan_id = fields.Many2one(
        "payment.plan", string="Plan", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    due_date = fields.Date(required=True)
    amount = fields.Monetary(
        string="Amount", currency_field="currency_id", required=True)
    currency_id = fields.Many2one(
        related="plan_id.currency_id", store=True, readonly=True)
    paid_amount = fields.Monetary(
        string="Paid", currency_field="currency_id")
    state = fields.Selection(
        [("pending", "Pending"), ("partial", "Partially Paid"),
         ("paid", "Paid"), ("cancelled", "Cancelled")],
        default="pending", required=True, index=True)
    payment_date = fields.Date()
    note = fields.Text()

    @api.depends("plan_id", "sequence")
    def _compute_name(self):
        for line in self:
            line.name = "%s / %s" % (
                line.plan_id.name or "", _("Installment")) \
                if line.plan_id else _("Installment")

    def action_register_payment(self):
        self.ensure_one()
        remaining = (self.amount or 0.0) - (self.paid_amount or 0.0)
        if remaining <= 0:
            return True
        return {
            "type": "ir.actions.act_window",
            "name": _("Register Payment"),
            "res_model": "account.payment.register",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": "account.move",
                "active_ids": [self.plan_id.move_id.id],
                "active_id": self.plan_id.move_id.id,
                "default_amount": remaining,
                "default_payment_date": self.due_date,
            },
        }

    def action_mark_paid(self):
        for line in self:
            line.paid_amount = line.amount
            line.state = "paid"
            line.payment_date = fields.Date.context_today(line)
        return True
