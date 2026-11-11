# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CoverageItem(models.Model):
    _name = "coverage.item"
    _description = "Coverage Item"
    _inherit = ["mail.thread"]
    _order = "coverage_days asc, id desc"

    name = fields.Char(
        string="Product", required=True, tracking=True,
        help="Product or item whose stock coverage is planned.")
    on_hand_qty = fields.Float(
        string="On Hand", required=True, default=0.0,
        help="Quantity currently available on hand.")
    daily_demand = fields.Float(
        string="Daily Demand", required=True, default=1.0,
        help="Average quantity consumed per day.")
    min_days = fields.Integer(
        string="Minimum Days", required=True, default=7,
        help="Minimum number of covered days to keep in stock.")
    coverage_days = fields.Float(
        string="Coverage Days", compute="_compute_coverage_days",
        store=True,
        help="Number of days the current stock covers at the daily demand.")
    below_minimum = fields.Boolean(
        string="Below Minimum", compute="_compute_coverage_days",
        store=True,
        help="True when covered days are below the minimum target.")
    planned_qty = fields.Float(
        string="Planned Purchase Qty", default=0.0,
        help="Quantity to purchase to restore healthy coverage.")
    state = fields.Selection(
        [("draft", "Draft"), ("planned", "Planned"),
         ("ordered", "Ordered")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("on_hand_qty", "daily_demand", "min_days")
    def _compute_coverage_days(self):
        for rec in self:
            if rec.daily_demand > 0:
                days = rec.on_hand_qty / rec.daily_demand
            else:
                days = 0.0
            rec.coverage_days = days
            rec.below_minimum = bool(days < rec.min_days)

    @api.constrains("daily_demand")
    def _check_daily_demand(self):
        for rec in self:
            if rec.daily_demand <= 0:
                raise ValidationError(_(
                    "The daily demand of %s must be above zero.",
                    rec.name))

    @api.constrains("min_days")
    def _check_min_days(self):
        for rec in self:
            if rec.min_days <= 0:
                raise ValidationError(_(
                    "The minimum days of %s must be above zero.",
                    rec.name))

    @api.constrains("on_hand_qty")
    def _check_on_hand_qty(self):
        for rec in self:
            if rec.on_hand_qty < 0:
                raise ValidationError(_(
                    "The on-hand quantity of %s cannot be negative.",
                    rec.name))

    @api.constrains("planned_qty", "state")
    def _check_planned_qty(self):
        for rec in self:
            if rec.state == "planned" and rec.planned_qty <= 0:
                raise ValidationError(_(
                    "Set a positive planned quantity before planning %s.",
                    rec.name))

    def action_plan(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(_(
                    "Only draft lines can be planned: %s.", rec.name))
            if rec.planned_qty <= 0:
                raise ValidationError(_(
                    "Set a positive planned quantity before planning %s.",
                    rec.name))
            rec.state = "planned"
            rec.message_post(body=_(
                "A planned purchase of %s was recorded.", rec.planned_qty))
        return True

    def action_mark_ordered(self):
        for rec in self:
            if rec.state != "planned":
                raise ValidationError(_(
                    "Only planned lines can be marked ordered: %s.",
                    rec.name))
            rec.state = "ordered"
            rec.message_post(body=_("The planned purchase was ordered."))
        return True

    def action_reset_draft(self):
        for rec in self:
            if rec.state == "draft":
                raise ValidationError(_(
                    "The line %s is already in draft.", rec.name))
            rec.state = "draft"
            rec.message_post(body=_("The line was reset to draft."))
        return True
