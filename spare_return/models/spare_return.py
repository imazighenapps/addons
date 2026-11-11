# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SpareReturn(models.Model):
    _name = "spare.return"
    _description = "Field Material Return"
    _inherit = ["mail.thread"]
    _order = "due_date, id"

    name = fields.Char(
        required=True, tracking=True,
        default=lambda self: _("Field Material"),
        help="Reference of the material sent to site.")
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True,
        help="Customer or site receiving the material.")
    site_name = fields.Char(
        string="Site", help="Site or location where the material was sent.")
    responsible_id = fields.Many2one(
        "res.users", string="Owner", default=lambda self: self.env.user,
        tracking=True, help="Person responsible for recovering the material.")
    sent_date = fields.Date(
        string="Sent On", required=True, default=fields.Date.context_today,
        tracking=True)
    due_date = fields.Date(
        string="Return Due", required=True, tracking=True,
        help="Date by which the unused material should be returned.")
    quantity_sent = fields.Float(
        string="Quantity Sent", required=True, default=1.0,
        help="Quantity sent to the site.")
    quantity_consumed = fields.Float(
        string="Consumed", default=0.0,
        help="Quantity consumed during the job.")
    quantity_returned = fields.Float(
        string="Returned", default=0.0,
        help="Quantity returned after the job.")
    quantity_outstanding = fields.Float(
        string="Outstanding", compute="_compute_quantities", store=True,
        help="Quantity still expected to come back.")
    state = fields.Selection(
        [("open", "Open"), ("returned", "Returned")],
        default="open", required=True, tracking=True, index=True)
    returned_on = fields.Date(string="Returned On", readonly=True, copy=False)
    is_overdue = fields.Boolean(
        string="Overdue", compute="_compute_is_overdue", store=True,
        help="Indicates that the return due date has passed.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("quantity_sent", "quantity_consumed", "quantity_returned")
    def _compute_quantities(self):
        for line in self:
            outstanding = (
                line.quantity_sent - line.quantity_consumed
                - line.quantity_returned)
            line.quantity_outstanding = max(outstanding, 0.0)

    @api.depends("due_date", "state")
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for line in self:
            line.is_overdue = bool(
                line.state == "open" and line.due_date
                and line.due_date < today)

    @api.constrains("quantity_sent", "quantity_consumed", "quantity_returned")
    def _check_quantities(self):
        for line in self:
            if line.quantity_sent <= 0:
                raise ValidationError(_(
                    "The sent quantity for %s must be greater than zero.",
                    line.name))
            if line.quantity_consumed < 0 or line.quantity_returned < 0:
                raise ValidationError(_(
                    "Consumed and returned quantities for %s cannot be "
                    "negative.", line.name))
            if line.quantity_consumed + line.quantity_returned > line.quantity_sent:
                raise ValidationError(_(
                    "Consumed and returned quantities for %s cannot exceed "
                    "what was sent.", line.name))

    @api.constrains("sent_date", "due_date", "returned_on")
    def _check_dates(self):
        for line in self:
            if line.due_date and line.sent_date \
                    and line.due_date < line.sent_date:
                raise ValidationError(_(
                    "The return due date of %s cannot be before the sent "
                    "date.", line.name))
            if line.returned_on and line.sent_date \
                    and line.returned_on < line.sent_date:
                raise ValidationError(_(
                    "The return date of %s cannot be before the sent date.",
                    line.name))

    def action_register_return(self):
        for line in self:
            if line.state == "returned":
                raise ValidationError(_(
                    "The material line %s is already returned.", line.name))
            returned_qty = line.quantity_sent - line.quantity_consumed
            line.write({
                "state": "returned",
                "quantity_returned": returned_qty,
                "returned_on": fields.Date.context_today(line),
            })
            line.message_post(body=_(
                "The remaining material has been returned."))
        return True
