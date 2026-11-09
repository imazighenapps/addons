# -*- coding: utf-8 -*-
from datetime import datetime, time

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SalesTarget(models.Model):
    _name = "sales.target"
    _description = "Sales Target"
    _inherit = ["mail.thread"]
    _order = "date_from desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: "Target %s"
        % fields.Date.context_today(self))
    user_id = fields.Many2one(
        "res.users", string="Salesperson", required=True,
        default=lambda self: self.env.user)
    team_id = fields.Many2one("crm.team", string="Team")
    date_from = fields.Date(
        required=True, default=fields.Date.context_today)
    date_to = fields.Date(required=True)
    target_amount = fields.Monetary(
        required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    achieved_amount = fields.Monetary(
        compute="_compute_achievement", string="Achieved",
        currency_field="currency_id", store=True)
    progress = fields.Float(
        compute="_compute_achievement", store=True,
        help="Percentage of the target already confirmed.")
    gap_amount = fields.Monetary(
        compute="_compute_achievement",
        currency_field="currency_id", store=True,
        help="Positive when the target is underachieved.")
    projected_amount = fields.Monetary(
        compute="_compute_achievement",
        currency_field="currency_id", store=True,
        help="Revenue expected at the end of period from the current pace.")
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"),
         ("done", "Done")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    note = fields.Text()

    _sql_constraints = [
        ('owner_period_uniq', "unique(user_id, date_from, date_to, company_id)", "This salesperson already carries a target for this period."),
    ]

    @api.constrains("target_amount")
    def _check_amount(self):
        for target in self:
            if target.target_amount <= 0.0:
                raise ValidationError(_(
                    "A target must be strictly positive."))

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for target in self:
            if target.date_to < target.date_from:
                raise ValidationError(_(
                    "The end date must follow the start date."))

    @api.depends("date_from", "date_to", "user_id", "company_id")
    def _compute_achievement(self):
        for target in self:
            achieved = target._achieved()
            days_total = (
                target.date_to - target.date_from).days + 1
            days_elapsed = (
                fields.Date.context_today(target)
                - target.date_from).days
            days_elapsed = min(days_elapsed, days_total)
            target.achieved_amount = achieved
            target.gap_amount = target.target_amount - achieved
            target.progress = (
                achieved / target.target_amount * 100.0
                if target.target_amount else 0.0)
            target.projected_amount = (
                achieved / days_elapsed * days_total
                if days_elapsed > 0 else achieved)

    def _achieved(self):
        self.ensure_one()
        end = datetime.combine(self.date_to, time(23, 59, 59))
        orders = self.env["sale.order"].search([
            ("state", "in", ("sale", "done")),
            ("date_order", ">=", self.date_from),
            ("date_order", "<=", end),
            ("company_id", "=", self.company_id.id),
        ])
        return sum(
            order.currency_id._convert(
                order.amount_untaxed, self.currency_id,
                self.company_id, fields.Date.context_today(self))
            for order in orders.filtered(
                lambda order: order.user_id == self.user_id))

    def action_start(self):
        for target in self:
            target.write({"state": "running"})
        return True

    def action_done(self):
        for target in self:
            if target.state not in ("running", "draft"):
                raise UserError(_(
                    "A target is closed from its running or draft state."))
            target.write({"state": "done"})
        return True

    def action_recompute(self):
        self._compute_achievement()
        return True
