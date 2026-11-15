# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MeetingAgendaLog(models.Model):
    _name = "meeting.agenda.log"
    _description = "Meeting Agenda"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "meeting_date desc, id desc"

    name = fields.Char(string="Title", required=True, tracking=True)
    meeting_date = fields.Date(
        string="Meeting Date", required=True, default=fields.Date.context_today,
        tracking=True, index=True)
    organizer_id = fields.Many2one(
        "res.users", string="Organizer", required=True,
        default=lambda self: self.env.user, tracking=True, index=True)
    attendee_names = fields.Char(string="Attendees", tracking=True)
    agenda = fields.Text(string="Agenda", required=True)
    outcomes = fields.Text(string="Outcomes / Decisions")
    action_items = fields.Text(string="Action Items")
    state = fields.Selection(
        [("draft", "Draft"), ("planned", "Planned"), ("done", "Done"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    def action_plan(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft meeting can be planned."))
            rec.state = "planned"

    def action_done(self):
        for rec in self:
            if rec.state not in ("draft", "planned"):
                raise UserError(_("Only a draft or planned meeting can be marked done."))
            rec.state = "done"

    def action_cancel(self):
        for rec in self:
            if rec.state == "cancelled":
                raise UserError(_("This meeting is already cancelled."))
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            if rec.state in ("draft", "planned"):
                raise UserError(_("This meeting can already be edited."))
            rec.state = "draft"
