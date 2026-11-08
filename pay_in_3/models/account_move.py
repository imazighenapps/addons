# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_plan_ids = fields.One2many(
        "payment.plan", "move_id", string="Payment Plans")
    payment_plan_count = fields.Integer(
        string="Plans", compute="_compute_payment_plan_count")

    @api.depends("payment_plan_ids")
    def _compute_payment_plan_count(self):
        for move in self:
            move.payment_plan_count = len(move.payment_plan_ids)

    def action_create_payment_plan(self):
        self.ensure_one()
        plan = self.env["payment.plan"].create({
            "move_id": self.id,
            "company_id": self.company_id.id,
            "total_amount": self.amount_total,
            "installment_count": 3,
            "first_due_date": self.invoice_date_due
            or fields.Date.context_today(self),
        })
        return {
            "type": "ir.actions.act_window",
            "name": _("Payment Plan"),
            "res_model": "payment.plan",
            "view_mode": "form",
            "res_id": plan.id,
        }

    def action_open_payment_plan(self):
        self.ensure_one()
        plan = self.payment_plan_ids.filtered(
            lambda p: p.state in ("draft", "active"))[:1]
        if not plan:
            return self.action_create_payment_plan()
        return {
            "type": "ir.actions.act_window",
            "name": _("Payment Plan"),
            "res_model": "payment.plan",
            "view_mode": "form",
            "res_id": plan.id,
        }
