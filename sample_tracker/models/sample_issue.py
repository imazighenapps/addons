# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SampleIssue(models.Model):
    _name = "sample.issue"
    _description = "Sample Hand-Out"
    _inherit = ["mail.thread"]
    _order = "handed_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Sample %s")
        % fields.Date.context_today(self),
        help="Reference of the hand-out, generated at creation.")
    item_id = fields.Many2one(
        "sample.item", string="Sample", required=True,
        ondelete="cascade", index=True, tracking=True)
    recipient_id = fields.Many2one(
        "res.partner", string="Recipient", required=True, tracking=True,
        help="Prospect or customer who received the sample.")
    quantity = fields.Integer(default=1, required=True,
                              help="Number of units handed out.")
    handed_on = fields.Date(
        string="Handed On", required=True, default=fields.Date.context_today,
        tracking=True)
    follow_up_on = fields.Date(
        string="Follow Up On", compute="_compute_follow_up", store=True,
        help="Date the call is due, from the follow-up delay of the "
             "sample.")
    state = fields.Selection(
        [("out", "With The Prospect"), ("consumed", "Consumed"),
         ("returned", "Returned")],
        default="out", required=True, copy=False, tracking=True,
        index=True)
    returned_on = fields.Date(
        string="Returned On", readonly=True, copy=False)
    converted = fields.Boolean(
        string="Order Placed", default=False, tracking=True,
        help="Ticked when the sample turned into a real order.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("item_id", "item_id.followup_days", "handed_on")
    def _compute_follow_up(self):
        for issue in self:
            if issue.item_id and issue.handed_on:
                issue.follow_up_on = issue.handed_on + relativedelta(
                    days=issue.item_id.followup_days)
            else:
                issue.follow_up_on = False

    @api.constrains("quantity")
    def _check_quantity(self):
        for issue in self:
            if issue.quantity <= 0:
                raise ValidationError(_(
                    "The quantity of %s handed to %s must be above "
                    "zero.", issue.item_id.name, issue.recipient_id.name))

    @api.constrains("handed_on", "returned_on")
    def _check_dates(self):
        for issue in self:
            if issue.returned_on and issue.returned_on < issue.handed_on:
                raise ValidationError(_(
                    "The return date of %s cannot come before the "
                    "hand-out date.", issue.name))

    def action_return(self):
        for issue in self:
            if issue.state != "out":
                raise UserError(_(
                    "The sample handed to %s is already closed.",
                    issue.recipient_id.name))
            issue.write({
                "state": "returned",
                "returned_on": fields.Date.context_today(issue),
            })
            issue.message_post(body=_(
                "The sample came back to the office."))
        return True

    def action_consume(self):
        for issue in self:
            if issue.state != "out":
                raise UserError(_(
                    "The sample handed to %s is already closed.",
                    issue.recipient_id.name))
            issue.write({"state": "consumed"})
            issue.message_post(body=_(
                "The sample was consumed by the test."))
        return True

    def action_convert(self):
        for issue in self:
            if issue.converted:
                raise UserError(_(
                    "The sample handed to %s is already attached to an "
                    "order.", issue.recipient_id.name))
            issue.write({"converted": True})
            issue.message_post(body=_(
                "The sample turned into an order."))
        return True
