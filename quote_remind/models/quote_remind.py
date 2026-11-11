# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class QuoteWatch(models.Model):
    _name = "quote.watch"
    _description = "Quotation Tracker"
    _inherit = ["mail.thread"]
    _order = "quote_on desc, id desc"

    name = fields.Char(
        default="/", required=True, copy=False, tracking=True,
        help="Reference of the tracker, generated from the QPW/ "
             "sequence.")
    quote_ref = fields.Char(
        string="Quotation Reference", required=True, tracking=True,
        help="Reference of the quotation being watched.")
    partner_id = fields.Many2one("res.partner", string="Customer")
    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", tracking=True,
        default=lambda self: self.env.user)
    quote_on = fields.Date(
        string="Sent On", required=True, default=fields.Date.context_today,
        tracking=True, help="Date the quotation was sent.")
    amount = fields.Monetary(tracking=True,
                             help="Amount of the quotation.")
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    remind_every = fields.Integer(
        string="Remind Every (days)", default=5, required=True,
        tracking=True, help="Days between two reminders.")
    max_reminders = fields.Integer(
        string="Max Reminders", default=3, required=True,
        help="Maximum number of reminders before the deal is left to "
             "die quietly.")
    state = fields.Selection(
        [("watching", "Watching"), ("won", "Won"), ("lost", "Lost")],
        default="watching", required=True, copy=False, tracking=True,
        index=True)
    nudge_ids = fields.One2many(
        "quote.nudge", "watch_id", string="Reminders")
    nudge_count = fields.Integer(
        string="Reminders", compute="_compute_nudges", store=True,
        help="Number of reminders already sent on this quotation.")
    last_nudge_on = fields.Date(
        string="Last Reminder", compute="_compute_nudges", store=True,
        help="Date of the most recent reminder.")
    is_due = fields.Boolean(
        string="Due", compute="_compute_is_due", store=True,
        help="True when the next reminder is late: the quotation needs "
             "a call today.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "quote.watch") or "/"
        return super().create(vals_list)

    @api.constrains("amount")
    def _check_amount(self):
        for watch in self:
            if watch.amount < 0:
                raise ValidationError(_(
                    "The amount of a quotation tracker cannot be negative."))

    @api.constrains("remind_every", "max_reminders")
    def _check_plan(self):
        for watch in self:
            if watch.remind_every <= 0:
                raise ValidationError(_(
                    "The reminder interval of %s must be above zero "
                    "days.", watch.name))
            if watch.max_reminders <= 0:
                raise ValidationError(_(
                    "The maximum number of reminders of %s must be "
                    "above zero.", watch.name))

    @api.depends("nudge_ids", "nudge_ids.nudge_on")
    def _compute_nudges(self):
        for watch in self:
            watch.nudge_count = len(watch.nudge_ids)
            dates = watch.nudge_ids.mapped("nudge_on")
            watch.last_nudge_on = max(dates) if dates else False

    @api.depends("quote_on", "remind_every", "state", "last_nudge_on",
                 "nudge_ids", "nudge_ids.nudge_on")
    def _compute_is_due(self):
        today = fields.Date.context_today(self)
        for watch in self:
            if watch.state != "watching":
                watch.is_due = False
                continue
            last = watch.last_nudge_on or watch.quote_on
            watch.is_due = bool(last) and (
                last + timedelta(days=watch.remind_every) <= today)

    def action_nudge(self):
        for watch in self:
            if watch.state != "watching":
                raise UserError(_(
                    "Only a quotation still being watched can be "
                    "reminded."))
            self.env["quote.nudge"].create({
                "watch_id": watch.id,
            })
            watch.message_post(body=_(
                "Reminder %s sent on the quotation %s.",
                watch.nudge_count, watch.quote_ref))
        return True

    def action_won(self):
        for watch in self:
            if watch.state != "watching":
                raise UserError(_(
                    "Only a quotation being watched can be closed as "
                    "won."))
            watch.state = "won"
            watch.message_post(body=_(
                "Quotation %s closed as won after %s reminder(s).",
                watch.quote_ref, watch.nudge_count))
        return True

    def action_lost(self):
        for watch in self:
            if watch.state != "watching":
                raise UserError(_(
                    "Only a quotation being watched can be closed as "
                    "lost."))
            watch.state = "lost"
            watch.message_post(body=_(
                "Quotation %s closed as lost after %s reminder(s).",
                watch.quote_ref, watch.nudge_count))
        return True


class QuoteNudge(models.Model):
    _name = "quote.nudge"
    _description = "Quotation Reminder"
    _inherit = ["mail.thread"]
    _order = "nudge_on desc, id desc"

    watch_id = fields.Many2one(
        "quote.watch", string="Quotation Tracker", required=True,
        ondelete="cascade", index=True)
    nudge_on = fields.Date(
        default=fields.Date.context_today, required=True,
        help="Date the reminder was sent.")
    channel = fields.Selection(
        [("email", "Email"), ("phone", "Phone"), ("meeting", "Meeting")],
        default="email", required=True,
        help="How the customer was reminded.")
    feedback = fields.Char(
        help="Outcome of the reminder, for example meeting booked.")
    user_id = fields.Many2one(
        "res.users", string="Reminder By", default=lambda self:
        self.env.user)
    company_id = fields.Many2one(
        related="watch_id.company_id", store=True, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        watch_ids = {vals["watch_id"] for vals in vals_list
                     if vals.get("watch_id")}
        if watch_ids:
            watching = self.env["quote.watch"].browse(
                sorted(watch_ids))
            for watch in watching:
                if watch.state != "watching":
                    raise UserError(_(
                        "The quotation %s is no longer watched: no "
                        "reminder can be sent.", watch.quote_ref))
                if watch.nudge_count >= watch.max_reminders:
                    raise UserError(_(
                        "The quotation %s already received its maximum "
                        "of %s reminder(s).", watch.quote_ref,
                        watch.max_reminders))
        return super().create(vals_list)
