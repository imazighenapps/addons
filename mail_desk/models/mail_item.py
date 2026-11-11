# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MailItem(models.Model):
    _name = "mail.item"
    _description = "Registered Mail Item"
    _inherit = ["mail.thread"]
    _order = "logged_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("MAIL %s")
        % fields.Date.context_today(self),
        help="Reference of the mail item, generated at creation.")
    direction = fields.Selection(
        [("inbound", "Inbound"), ("outbound", "Outbound")],
        default="inbound", required=True, tracking=True, index=True,
        help="Whether the mail entered or left the company.")
    partner_name = fields.Char(
        string="Sender / Recipient", required=True, tracking=True,
        help="Sender for inbound mail or recipient for outbound mail.")
    tracking_number = fields.Char(
        string="Tracking Number", tracking=True,
        help="Tracking or registered reference provided by the carrier.")
    logged_on = fields.Date(
        string="Logged On", required=True,
        default=fields.Date.context_today, tracking=True)
    collected_on = fields.Date(
        string="Collected On", readonly=True, copy=False, tracking=True)
    collected_by = fields.Char(
        string="Collected By", readonly=True, copy=False, tracking=True,
        help="Person who collected or received the item.")
    state = fields.Selection(
        [("waiting", "Waiting"), ("collected", "Collected")],
        default="waiting", required=True, copy=False, tracking=True,
        index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company, index=True)
    note = fields.Text()

    @api.constrains("logged_on", "collected_on")
    def _check_dates(self):
        for record in self:
            if record.collected_on and record.collected_on < record.logged_on:
                raise ValidationError(_(
                    "The collection date of %s cannot come before the "
                    "logged date.", record.name))

    def action_collect(self):
        for record in self:
            if record.state != "waiting":
                raise ValidationError(_(
                    "The mail item %s is already collected.", record.name))
            record.write({
                "state": "collected",
                "collected_on": fields.Date.context_today(record),
                "collected_by": self.env.user.name,
            })
            record.message_post(body=_(
                "The mail item was collected."))
        return True
