# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DemandPlan(models.Model):
    _name = "demand.plan"
    _description = "Sales Forecast Plan"
    _inherit = ["mail.thread"]
    _order = "period_start desc, id desc"

    name = fields.Char(
        required=True, tracking=True,
        default=lambda self: _("Forecast %s")
        % fields.Date.context_today(self))
    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", required=True,
        default=lambda self: self.env.user, tracking=True, index=True)
    period_start = fields.Date(
        string="Period Start", required=True, tracking=True)
    period_end = fields.Date(
        string="Period End", required=True, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("committed", "Committed"),
         ("closed", "Closed")],
        default="draft", required=True, tracking=True, index=True)
    line_ids = fields.One2many(
        "demand.plan.line", "plan_id", string="Forecast Lines", copy=True)
    line_count = fields.Integer(
        string="Lines", compute="_compute_totals", store=True)
    forecast_qty = fields.Float(
        string="Forecast Qty", compute="_compute_totals", store=True)
    actual_qty = fields.Float(
        string="Actual Qty", compute="_compute_totals", store=True)
    variance_qty = fields.Float(
        string="Variance Qty", compute="_compute_totals", store=True)
    forecast_amount = fields.Monetary(
        string="Forecast Amount", compute="_compute_totals",
        store=True, currency_field="currency_id")
    actual_amount = fields.Monetary(
        string="Actual Amount", compute="_compute_totals",
        store=True, currency_field="currency_id")
    variance_amount = fields.Monetary(
        string="Variance Amount", compute="_compute_totals",
        store=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends(
        "line_ids", "line_ids.forecast_qty", "line_ids.actual_qty",
        "line_ids.forecast_amount", "line_ids.actual_amount",
        "line_ids.variance_qty", "line_ids.variance_amount")
    def _compute_totals(self):
        for plan in self:
            lines = plan.line_ids
            plan.line_count = len(lines)
            plan.forecast_qty = sum(lines.mapped("forecast_qty"))
            plan.actual_qty = sum(lines.mapped("actual_qty"))
            plan.variance_qty = sum(lines.mapped("variance_qty"))
            plan.forecast_amount = sum(lines.mapped("forecast_amount"))
            plan.actual_amount = sum(lines.mapped("actual_amount"))
            plan.variance_amount = sum(lines.mapped("variance_amount"))

    @api.constrains("period_start", "period_end")
    def _check_period(self):
        for plan in self:
            if plan.period_end < plan.period_start:
                raise ValidationError(_(
                    "The end of plan %s cannot come before its start.",
                    plan.name))

    def action_commit(self):
        for plan in self:
            if plan.state != "draft":
                raise UserError(_(
                    "Only draft plans can be committed."))
            if not plan.line_ids:
                raise UserError(_(
                    "Plan %s must contain at least one forecast line "
                    "before it is committed.", plan.name))
            plan.state = "committed"
            plan.message_post(body=_("The forecast was committed."))
        return True

    def action_close(self):
        for plan in self:
            if plan.state != "committed":
                raise UserError(_(
                    "Only committed plans can be closed."))
            plan.state = "closed"
            plan.message_post(body=_("The forecast was closed."))
        return True

    def action_reset_draft(self):
        for plan in self:
            if plan.state != "committed":
                raise UserError(_(
                    "Only committed plans can be reset to draft."))
            plan.state = "draft"
            plan.message_post(body=_("The forecast was reset to draft."))
        return True
