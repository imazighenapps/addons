# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class RoomBooking(models.Model):
    _name = "room.booking"
    _description = "Room Booking"
    _inherit = ["mail.thread"]
    _order = "start_at desc, id desc"

    name = fields.Char(
        string="Subject", required=True, tracking=True,
        help="Purpose of the meeting held in the room.")
    room_id = fields.Many2one(
        "room.room", string="Room", required=True, ondelete="cascade",
        index=True, tracking=True)
    host_id = fields.Many2one(
        "res.users", string="Host", required=True, tracking=True,
        default=lambda self: self.env.user)
    start_at = fields.Datetime(
        string="Start", required=True, tracking=True,
        default=fields.Datetime.now)
    end_at = fields.Datetime(
        string="End", required=True, tracking=True)
    attendee_count = fields.Integer(
        string="Attendees", default=1,
        help="Expected number of people attending the meeting.")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("start_at", "end_at")
    def _check_dates(self):
        for booking in self:
            if booking.end_at and booking.start_at \
                    and booking.end_at <= booking.start_at:
                raise ValidationError(_(
                    "The end of booking \"%s\" must be after its start.",
                    booking.name))

    @api.constrains("attendee_count")
    def _check_attendees(self):
        for booking in self:
            if booking.attendee_count <= 0:
                raise ValidationError(_(
                    "The attendee count of booking \"%s\" must be above zero.",
                    booking.name))

    @api.constrains("room_id", "start_at", "end_at", "state", "company_id")
    def _check_overlap(self):
        for booking in self:
            if booking.state != "confirmed" or not booking.room_id \
                    or not booking.start_at or not booking.end_at:
                continue
            overlap = self.search([
                ("id", "!=", booking.id),
                ("room_id", "=", booking.room_id.id),
                ("state", "=", "confirmed"),
                ("start_at", "<", booking.end_at),
                ("end_at", ">", booking.start_at),
            ], limit=1)
            if overlap:
                raise ValidationError(_(
                    "Room \"%s\" is already booked by \"%s\" during this "
                    "time slot.", booking.room_id.name, overlap.name))

    def action_confirm(self):
        for booking in self:
            if booking.state != "draft":
                raise UserError(_(
                    "Only a draft booking can be confirmed."))
            booking.state = "confirmed"
            booking.message_post(body=_("The booking has been confirmed."))
        return True

    def action_cancel(self):
        for booking in self:
            if booking.state == "cancelled":
                raise UserError(_("This booking is already cancelled."))
            booking.state = "cancelled"
            booking.message_post(body=_("The booking has been cancelled."))
        return True

    def action_reset(self):
        for booking in self:
            if booking.state != "cancelled":
                raise UserError(_(
                    "Only a cancelled booking can be reset to draft."))
            booking.state = "draft"
            booking.message_post(body=_("The booking has been reset to draft."))
        return True
