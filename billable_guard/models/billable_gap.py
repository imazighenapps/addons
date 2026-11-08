# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class BillableGap(models.Model):
    _name = "billable.gap"
    _description = "Unbilled Time"
    _inherit = ["mail.thread"]
    _order = "date_from desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    project_id = fields.Many2one(
        "project.project", string="Project", required=True)
    task_id = fields.Many2one("project.task", string="Task")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    partner_id = fields.Many2one(
        related="project_id.partner_id", store=True, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    sale_line_id = fields.Many2one(
        "sale.order.line", string="Sales Order Line")
    sale_order_id = fields.Many2one(
        related="sale_line_id.order_id", store=True, readonly=True)
    hours_logged = fields.Float(string="Hours Logged")
    hours_invoiced = fields.Float(string="Hours Invoiced")
    hours_gap = fields.Float(
        string="Hours Not Billed", compute="_compute_gap", store=True)
    amount_at_risk = fields.Monetary(
        string="Amount at Risk", currency_field="currency_id",
        compute="_compute_gap", store=True)
    state = fields.Selection(
        [("open", "Open"), ("invoiced", "Invoiced"), ("ignored", "Ignored")],
        default="open", required=True, tracking=True, index=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    note = fields.Text()

    @api.depends("hours_logged", "hours_invoiced", "sale_line_id",
                 "sale_line_id.price_unit")
    def _compute_gap(self):
        for gap in self:
            gap.hours_gap = (gap.hours_logged or 0.0) \
                - (gap.hours_invoiced or 0.0)
            price = gap.sale_line_id.price_unit if gap.sale_line_id else 0.0
            gap.amount_at_risk = max(gap.hours_gap, 0.0) * price

    @api.depends("project_id", "task_id", "employee_id")
    def _compute_name(self):
        for gap in self:
            parts = [
                gap.project_id.name or "",
                gap.task_id.name or "",
                gap.employee_id.name or "",
            ]
            gap.name = " / ".join(part for part in parts if part) \
                or _("Unbilled Time")

    def action_ignore(self):
        for gap in self:
            gap.state = "ignored"
        return True

    def action_reopen(self):
        for gap in self:
            gap.state = "open"
        return True

    def action_create_invoice(self):
        self.ensure_one()
        if not self.sale_order_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Create Invoice"),
            "res_model": "sale.advance.payment.inv",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": "sale.order",
                "active_ids": [self.sale_order_id.id],
                "active_id": self.sale_order_id.id,
                "default_advance_payment_method": "delivered",
            },
        }
