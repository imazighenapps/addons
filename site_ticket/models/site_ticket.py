# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SiteTicket(models.Model):
    _name = "site.ticket"
    _description = "Building Ticket"
    _inherit = ["mail.thread"]
    _order = "priority desc, requested_on, id desc"

    name = fields.Char(
        string="Issue", required=True, tracking=True,
        help="Short description of the building problem.")
    area_id = fields.Many2one(
        "site.area", string="Area", required=True, ondelete="cascade",
        index=True, tracking=True)
    owner_id = fields.Many2one(
        "res.users", string="Owner", tracking=True,
        default=lambda self: self.env.user)
    contractor_id = fields.Many2one(
        "res.partner", string="Contractor",
        help="External contractor in charge of fixing the issue.")
    priority = fields.Selection(
        [("0", "Low"), ("1", "Normal"), ("2", "High"), ("3", "Urgent")],
        default="1", required=True, tracking=True)
    requested_on = fields.Date(
        string="Requested On", required=True,
        default=fields.Date.context_today, tracking=True)
    deadline_on = fields.Date(string="Deadline", tracking=True)
    started_on = fields.Date(string="Started On", readonly=True, copy=False)
    resolved_on = fields.Date(string="Resolved On", readonly=True, copy=False)
    cost = fields.Monetary(
        string="Cost", currency_field="currency_id",
        help="Estimated or actual repair cost.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("new", "New"), ("in_progress", "In Progress"),
         ("done", "Done"), ("cancelled", "Cancelled")],
        default="new", required=True, tracking=True, index=True)
    photo_note = fields.Text(
        string="Photo / Evidence",
        help="Describe the photos or evidence attached to the ticket.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.constrains("requested_on", "deadline_on", "resolved_on")
    def _check_dates(self):
        for ticket in self:
            if ticket.deadline_on and ticket.requested_on \
                    and ticket.deadline_on < ticket.requested_on:
                raise ValidationError(_(
                    "The deadline of ticket \"%s\" cannot be before the "
                    "request date.", ticket.name))
            if ticket.resolved_on and ticket.requested_on \
                    and ticket.resolved_on < ticket.requested_on:
                raise ValidationError(_(
                    "The resolution date of ticket \"%s\" cannot be before "
                    "the request date.", ticket.name))

    @api.constrains("cost")
    def _check_cost(self):
        for ticket in self:
            if ticket.cost < 0:
                raise ValidationError(_(
                    "The cost of ticket \"%s\" cannot be negative.",
                    ticket.name))

    def action_start(self):
        for ticket in self:
            if ticket.state != "new":
                raise UserError(_(
                    "Only a new ticket can be started."))
            ticket.write({
                "state": "in_progress",
                "started_on": fields.Date.context_today(ticket),
            })
            ticket.message_post(body=_("The ticket is now in progress."))
        return True

    def action_done(self):
        for ticket in self:
            if ticket.state != "in_progress":
                raise UserError(_(
                    "Only a ticket in progress can be marked as done."))
            ticket.write({
                "state": "done",
                "resolved_on": fields.Date.context_today(ticket),
            })
            ticket.message_post(body=_("The ticket has been resolved."))
        return True

    def action_cancel(self):
        for ticket in self:
            if ticket.state in ("done", "cancelled"):
                raise UserError(_(
                    "A done or cancelled ticket cannot be cancelled again."))
            ticket.state = "cancelled"
            ticket.message_post(body=_("The ticket has been cancelled."))
        return True

    def action_reset(self):
        for ticket in self:
            if ticket.state != "cancelled":
                raise UserError(_(
                    "Only a cancelled ticket can be reset to new."))
            ticket.write({
                "state": "new",
                "started_on": False,
                "resolved_on": False,
            })
            ticket.message_post(body=_("The ticket has been reset to new."))
        return True
