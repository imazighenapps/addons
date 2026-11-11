# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RetainerBank(models.Model):
    _name = "retainer.bank"
    _description = "Retainer Bank"
    _inherit = ["mail.thread"]
    _order = "date_end, id desc"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True, index=True)
    date_start = fields.Date(string="Start Date", required=True, tracking=True)
    date_end = fields.Date(string="End Date", required=True, tracking=True)
    hours_purchased = fields.Float(
        string="Hours Purchased", required=True, tracking=True)
    alert_hours = fields.Float(
        string="Low Balance Threshold", default=5.0,
        help="Remaining hours at or below this value flag the bank as low.")
    usage_ids = fields.One2many("retainer.usage", "bank_id", string="Usage")
    hours_used = fields.Float(
        string="Hours Used", compute="_compute_balance", store=True)
    hours_remaining = fields.Float(
        string="Hours Remaining", compute="_compute_balance", store=True)
    burn_rate = fields.Float(
        string="Burn Rate (%)", compute="_compute_balance", store=True)
    is_low = fields.Boolean(
        string="Low Balance", compute="_compute_balance", store=True)
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")],
        default="open", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True)
    note = fields.Text()

    @api.depends("hours_purchased", "alert_hours", "usage_ids.hours", "state")
    def _compute_balance(self):
        for bank in self:
            used = sum(bank.usage_ids.mapped("hours"))
            purchased = bank.hours_purchased or 0.0
            remaining = purchased - used
            bank.hours_used = used
            bank.hours_remaining = remaining
            bank.burn_rate = (used / purchased * 100.0) if purchased else 0.0
            bank.is_low = bool(bank.state == "open" and remaining <= bank.alert_hours)

    @api.constrains("hours_purchased", "alert_hours")
    def _check_amounts(self):
        for bank in self:
            if bank.hours_purchased <= 0:
                raise ValidationError(_(
                    "The purchased hours of %s must be above zero.", bank.name))
            if bank.alert_hours < 0:
                raise ValidationError(_(
                    "The low balance threshold of %s cannot be negative.", bank.name))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for bank in self:
            if bank.date_end < bank.date_start:
                raise ValidationError(_(
                    "The end date of %s cannot come before its start date.",
                    bank.name))

    def action_close(self):
        for bank in self:
            if bank.state != "open":
                raise ValidationError(_("Only an open retainer can be closed."))
            bank.state = "closed"
        return True

    def action_reopen(self):
        for bank in self:
            if bank.state != "closed":
                raise ValidationError(_("Only a closed retainer can be reopened."))
            bank.state = "open"
        return True
