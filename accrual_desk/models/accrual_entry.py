# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccrualEntry(models.Model):
    _name = "accrual.entry"
    _description = "Accrual Entry"
    _inherit = ["mail.thread"]
    _order = "period_date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", tracking=True,
        help="Supplier or party the service was received from.")
    owner_id = fields.Many2one(
        "res.users", string="Owner", tracking=True,
        default=lambda self: self.env.user,
        help="Person responsible for booking and reversing this accrual.")
    period_date = fields.Date(
        string="Period", required=True, tracking=True,
        default=fields.Date.context_today,
        help="Accounting period this accrual belongs to.")
    reverse_on = fields.Date(
        string="Planned Reversal", required=True, tracking=True,
        help="Date on which the accrual should be reversed.")
    booked_on = fields.Date(string="Booked On", readonly=True, copy=False)
    reversed_on = fields.Date(string="Reversed On", readonly=True, copy=False)
    amount = fields.Monetary(required=True, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("booked", "Booked"),
         ("reversed", "Reversed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.onchange("period_date")
    def _onchange_period_date(self):
        for entry in self:
            if entry.period_date and not entry.reverse_on:
                entry.reverse_on = entry.period_date + relativedelta(months=1)

    @api.constrains("amount")
    def _check_amount(self):
        for entry in self:
            if entry.amount <= 0:
                raise ValidationError(_(
                    "The amount of accrual %s must be greater than zero.",
                    entry.name))

    @api.constrains("period_date", "reverse_on")
    def _check_dates(self):
        for entry in self:
            if entry.reverse_on and entry.period_date \
                    and entry.reverse_on < entry.period_date:
                raise ValidationError(_(
                    "The reversal date of %s cannot come before its period.",
                    entry.name))

    def action_book(self):
        for entry in self:
            if entry.state != "draft":
                raise ValidationError(_(
                    "Only a draft accrual can be booked."))
            entry.write({
                "state": "booked",
                "booked_on": fields.Date.context_today(entry),
            })
            entry.message_post(body=_("Accrual booked for the period."))
        return True

    def action_reverse(self):
        for entry in self:
            if entry.state != "booked":
                raise ValidationError(_(
                    "Only a booked accrual can be reversed."))
            entry.write({
                "state": "reversed",
                "reversed_on": fields.Date.context_today(entry),
            })
            entry.message_post(body=_("Accrual reversed."))
        return True

    def action_reset(self):
        for entry in self:
            if entry.state == "booked":
                raise ValidationError(_(
                    "A booked accrual cannot be reset to draft. Reverse it "
                    "first."))
            entry.write({"state": "draft", "reversed_on": False})
            entry.message_post(body=_("Accrual reset to draft."))
        return True
