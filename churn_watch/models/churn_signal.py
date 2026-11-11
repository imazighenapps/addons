# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ChurnSignal(models.Model):
    _name = "churn.signal"
    _description = "Churn Risk Signal"
    _inherit = ["mail.thread"]
    _order = "days_silent desc, id desc"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True,
        index=True)
    last_order_date = fields.Date(
        string="Last Order Date", required=True, tracking=True,
        default=fields.Date.context_today)
    silence_threshold = fields.Integer(
        string="Silence Threshold (days)", required=True, default=30,
        help="Number of days without activity before the customer is at risk.")
    days_silent = fields.Integer(
        string="Days Silent", compute="_compute_risk", store=True,
        help="Days since the last recorded order date.")
    is_at_risk = fields.Boolean(
        string="At Risk", compute="_compute_risk", store=True, index=True,
        help="True when the silent days reach the configured threshold.")
    action_ids = fields.One2many(
        "churn.action", "signal_id", string="Save Actions")
    action_count = fields.Integer(
        string="Actions", compute="_compute_action_count", store=True)
    state = fields.Selection(
        [("watching", "Watching"), ("saved", "Saved"), ("lost", "Lost")],
        default="watching", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("last_order_date", "silence_threshold")
    def _compute_risk(self):
        today = fields.Date.context_today(self)
        for signal in self:
            if signal.last_order_date:
                delta = (today - signal.last_order_date).days
                signal.days_silent = max(delta, 0)
            else:
                signal.days_silent = 0
            signal.is_at_risk = signal.days_silent >= signal.silence_threshold

    @api.depends("action_ids")
    def _compute_action_count(self):
        for signal in self:
            signal.action_count = len(signal.action_ids)

    @api.constrains("silence_threshold")
    def _check_threshold(self):
        for signal in self:
            if signal.silence_threshold <= 0:
                raise ValidationError(_(
                    "The silence threshold of %s must be above zero.",
                    signal.name))

    @api.constrains("last_order_date")
    def _check_last_order_date(self):
        today = fields.Date.context_today(self)
        for signal in self:
            if signal.last_order_date and signal.last_order_date > today:
                raise ValidationError(_(
                    "The last order date of %s cannot be in the future.",
                    signal.name))

    def action_mark_saved(self):
        for signal in self:
            signal.write({"state": "saved"})
            signal.message_post(body=_("The customer signal has been saved."))
        return True

    def action_mark_lost(self):
        for signal in self:
            signal.write({"state": "lost"})
            signal.message_post(body=_("The customer has been marked as lost."))
        return True
