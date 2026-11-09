# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MeetingMinute(models.Model):
    _name = "meeting.minute"
    _description = "Meeting Minutes"
    _inherit = ["mail.thread"]
    _order = "date_meeting desc, id desc"

    name = fields.Char(required=True, tracking=True)
    date_meeting = fields.Datetime(
        string="Meeting Date", required=True,
        default=fields.Datetime.now, tracking=True)
    location = fields.Char()
    chair_id = fields.Many2one(
        "res.users", string="Chair", required=True, tracking=True,
        default=lambda self: self.env.user)
    attendee_ids = fields.Many2many(
        "res.partner", "meeting_minute_attendee_rel", "minute_id",
        "partner_id", string="Attendees",
        help="People who attended the meeting.")
    agenda = fields.Text(help="Points discussed during the meeting.")
    decisions = fields.Text(
        help="What was decided. Required before the minutes can be closed.")
    state = fields.Selection(
        [("draft", "Draft"), ("held", "Held"), ("closed", "Closed"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    action_ids = fields.One2many(
        "meeting.action", "minute_id", string="Action Items", copy=True)
    action_count = fields.Integer(compute="_compute_action_counts")
    open_action_count = fields.Integer(
        string="Open Actions", compute="_compute_action_counts")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    @api.depends("action_ids.state")
    def _compute_action_counts(self):
        for minute in self:
            minute.action_count = len(minute.action_ids)
            minute.open_action_count = len(minute.action_ids.filtered(
                lambda action: action.state == "todo"))

    def action_hold(self):
        for minute in self:
            if minute.state != "draft":
                raise UserError(_(
                    "Only a draft minute can be marked as held."))
            minute.state = "held"
            minute.message_post(body=_(
                "Meeting held with %s attendee(s).",
                len(minute.attendee_ids)))
        return True

    def action_close(self):
        for minute in self:
            if minute.state != "held":
                raise UserError(_("Only a held minute can be closed."))
            if not (minute.decisions or "").strip():
                raise UserError(_(
                    "Record the decisions of the meeting before closing the "
                    "minutes."))
            minute.state = "closed"
            minute.message_post(body=_(
                "Minutes closed: %s action(s) are still open.",
                minute.open_action_count))
        return True

    def action_cancel(self):
        for minute in self:
            if minute.state not in ("draft", "held"):
                raise UserError(_(
                    "Only a draft or held minute can be cancelled."))
            minute.state = "cancelled"
            minute.message_post(body=_("Minutes cancelled."))
        return True

    def action_reset(self):
        for minute in self:
            if minute.state == "draft":
                raise UserError(_("The minutes are already in draft."))
            minute.state = "draft"
            minute.message_post(body=_("Minutes reset to draft."))
        return True


class MeetingAction(models.Model):
    _name = "meeting.action"
    _description = "Meeting Action Item"
    _order = "minute_id, sequence, id"

    minute_id = fields.Many2one(
        "meeting.minute", string="Meeting Minutes", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Action", required=True)
    user_id = fields.Many2one(
        "res.users", string="Assigned To", required=True,
        default=lambda self: self.env.user)
    due_date = fields.Date(string="Due Date")
    state = fields.Selection(
        [("todo", "To Do"), ("done", "Done"), ("cancelled", "Cancelled")],
        default="todo", required=True, index=True)
    done_date = fields.Date(string="Done On", readonly=True)
    is_overdue = fields.Boolean(
        compute="_compute_is_overdue", store=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        related="minute_id.company_id", store=True, readonly=True)

    @api.depends("due_date", "state")
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for action in self:
            action.is_overdue = bool(
                action.due_date and action.due_date < today
                and action.state == "todo")

    def action_done(self):
        today = fields.Date.context_today(self)
        for action in self:
            if action.state == "done":
                raise UserError(_(
                    "The action \"%s\" is already done.", action.name))
            if action.state == "cancelled":
                raise UserError(_(
                    "The cancelled action \"%s\" cannot be marked as done.",
                    action.name))
            action.state = "done"
            action.done_date = today
        return True

    def action_reopen(self):
        for action in self:
            if action.state != "done":
                raise UserError(_(
                    "Only a done action can be reopened."))
            action.state = "todo"
            action.done_date = False
        return True

    def action_cancel(self):
        for action in self:
            if action.state == "cancelled":
                raise UserError(_(
                    "The action \"%s\" is already cancelled.", action.name))
            action.state = "cancelled"
        return True
