# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MeetingRoom(models.Model):
    _name = "meeting.room"
    _description = "Meeting Room"
    _order = "name, id"

    name = fields.Char(required=True)
    capacity = fields.Integer(string="Capacity")
    location = fields.Char(string="Location")
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    _name_company_uniq = models.Constraint(
        "UNIQUE(name, company_id)",
        "A room with this name already exists for this company.")


class MeetingBooking(models.Model):
    _name = "meeting.booking"
    _description = "Meeting Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_datetime desc, id desc"

    name = fields.Char(string="Subject", required=True, tracking=True)
    room_id = fields.Many2one(
        "meeting.room", string="Room", required=True, index=True, tracking=True)
    organizer_id = fields.Many2one(
        "res.users", string="Organizer", default=lambda self: self.env.user,
        required=True, tracking=True)
    start_datetime = fields.Datetime(
        string="Start", required=True, tracking=True)
    stop_datetime = fields.Datetime(
        string="End", required=True, tracking=True)
    attendee_count = fields.Integer(string="Attendees")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("start_datetime", "stop_datetime")
    def _check_dates(self):
        for rec in self:
            if rec.start_datetime and rec.stop_datetime and rec.stop_datetime <= rec.start_datetime:
                raise ValidationError(
                    _("The end time must be after the start time."))

    @api.constrains("room_id", "start_datetime", "stop_datetime", "state", "company_id")
    def _check_overlap(self):
        for rec in self:
            if rec.state != "confirmed" or not rec.room_id:
                continue
            domain = [
                ("id", "!=", rec.id),
                ("room_id", "=", rec.room_id.id),
                ("state", "=", "confirmed"),
                ("start_datetime", "<", rec.stop_datetime),
                ("stop_datetime", ">", rec.start_datetime),
            ]
            if rec.company_id:
                domain.append(("company_id", "=", rec.company_id.id))
            other = self.search(domain, limit=1)
            if other:
                raise ValidationError(
                    _("Room %(room)s is already booked during this time (%(name)s).",
                      room=rec.room_id.display_name, name=other.name))

    def action_confirm(self):
        for rec in self:
            if rec.state == "cancelled":
                raise UserError(_("A cancelled booking cannot be confirmed."))
            rec.state = "confirmed"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
