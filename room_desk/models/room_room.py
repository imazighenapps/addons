# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RoomRoom(models.Model):
    _name = "room.room"
    _description = "Meeting Room"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Short room code printed on the door, for example R-201.")
    location = fields.Char(
        help="Floor, building or zone where the room is located.")
    capacity = fields.Integer(
        required=True, default=1,
        help="Maximum number of people the room can host.")
    equipment = fields.Char(
        help="Main equipment available, for example projector and screen.")
    booking_ids = fields.One2many(
        "room.booking", "room_id", string="Bookings")
    booking_count = fields.Integer(
        string="Bookings", compute="_compute_booking_counts", store=True)
    upcoming_count = fields.Integer(
        string="Upcoming", compute="_compute_booking_counts", store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("booking_ids", "booking_ids.state", "booking_ids.start_at")
    def _compute_booking_counts(self):
        today = fields.Datetime.now()
        for room in self:
            bookings = room.booking_ids
            room.booking_count = len(bookings)
            room.upcoming_count = len(bookings.filtered(
                lambda booking: booking.state == "confirmed"
                and booking.start_at >= today))
