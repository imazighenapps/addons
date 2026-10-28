# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


WEEKDAYS = [
    ("0", "Monday"),
    ("1", "Tuesday"),
    ("2", "Wednesday"),
    ("3", "Thursday"),
    ("4", "Friday"),
    ("5", "Saturday"),
    ("6", "Sunday"),
]
WEEKDAY_LABELS = dict(WEEKDAYS)


class DeliveryTimeSlot(models.Model):
    _name = "delivery.time.slot"
    _description = "Delivery Time Slot"
    _inherit = ["mail.thread"]
    _order = "weekday, start_hour, id"

    name = fields.Char(required=True, tracking=True)
    weekday = fields.Selection(
        WEEKDAYS, required=True, tracking=True,
        help="Day of the week this window is open.")
    start_hour = fields.Float(
        required=True, tracking=True,
        help="Start of the window, for example 8.5 = 08:30.")
    end_hour = fields.Float(
        required=True, tracking=True,
        help="End of the window, for example 12.0 = 12:00.")
    capacity = fields.Integer(
        required=True, default=8, tracking=True,
        help="Maximum number of bookings per date.")
    location = fields.Char(
        help="Dock or warehouse where the delivery is unloaded.")
    active = fields.Boolean(default=True)
    booking_ids = fields.One2many(
        "delivery.time.booking", "slot_id", string="Bookings", copy=False)
    booking_count = fields.Integer(
        string="Open Bookings", compute="_compute_counts",
        help="Draft, confirmed and done bookings of this slot.")
    available_count = fields.Integer(
        string="Places Left Today", compute="_compute_counts",
        help="Capacity minus the bookings confirmed for today.")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    @api.depends("booking_ids.state", "booking_ids.date", "capacity")
    def _compute_counts(self):
        today = fields.Date.context_today(self)
        for slot in self:
            bookings = slot.booking_ids
            open_bookings = bookings.filtered(
                lambda booking: booking.state in
                ("draft", "confirmed", "done"))
            confirmed_today = bookings.filtered(
                lambda booking: booking.state == "confirmed"
                and booking.date == today)
            slot.booking_count = len(open_bookings)
            slot.available_count = slot.capacity - len(confirmed_today)

    @api.constrains("start_hour", "end_hour")
    def _check_hours(self):
        for slot in self:
            if slot.start_hour < 0.0 or slot.start_hour >= 24.0:
                raise ValidationError(_(
                    "On slot \"%s\", the start hour must be between 0:00 "
                    "and 24:00.", slot.name))
            if slot.end_hour > 24.0:
                raise ValidationError(_(
                    "On slot \"%s\", the end hour cannot be after 24:00.",
                    slot.name))
            if slot.end_hour <= slot.start_hour:
                raise ValidationError(_(
                    "On slot \"%s\", the end hour must be after the start "
                    "hour.", slot.name))

    @api.constrains("capacity")
    def _check_capacity(self):
        for slot in self:
            if slot.capacity <= 0:
                raise ValidationError(_(
                    "On slot \"%s\", the capacity must be strictly positive.",
                    slot.name))

    def action_activate(self):
        for slot in self:
            if not slot.active:
                slot.active = True
        return True

    def action_archive(self):
        for slot in self:
            if slot.active:
                slot.active = False
        return True


class DeliveryTimeBooking(models.Model):
    _name = "delivery.time.booking"
    _description = "Delivery Booking"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(
        default="/", required=True, copy=False, tracking=True)
    slot_id = fields.Many2one(
        "delivery.time.slot", string="Time Slot", required=True,
        ondelete="restrict", tracking=True, index=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True)
    reference = fields.Char(
        help="Sale order or delivery reference, for example S00042.")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"),
         ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    user_id = fields.Many2one(
        "res.users", string="Booked by", default=lambda self: self.env.user)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "delivery.time.booking") or "/"
        return super().create(vals_list)

    @api.constrains("date", "slot_id")
    def _check_slot_weekday(self):
        for booking in self:
            if not booking.date or not booking.slot_id:
                continue
            if str(booking.date.weekday()) != booking.slot_id.weekday:
                raise ValidationError(_(
                    "The date %(date)s is a %(day)s: the slot \"%(slot)s\" "
                    "is only open on %(slot_day)s.",
                    date=booking.date,
                    day=WEEKDAY_LABELS.get(
                        str(booking.date.weekday()), ""),
                    slot=booking.slot_id.name,
                    slot_day=WEEKDAY_LABELS.get(
                        booking.slot_id.weekday, "")))

    def _availability_error(self):
        """Return why this booking cannot be confirmed, or None."""
        self.ensure_one()
        slot = self.slot_id
        if not slot or not self.date:
            return None
        # A blackout closes the physical dock: it applies to every company.
        blackout = self.env["delivery.time.blackout"].search([
            ("date", "=", self.date),
            ("active", "=", True),
            "|",
            ("slot_id", "=", False),
            ("slot_id", "=", slot.id),
        ], limit=1)
        if blackout:
            return _(
                "The date %(date)s is a blackout day for \"%(slot)s\" "
                "(%(name)s).",
                date=self.date, slot=slot.name, name=blackout.name)
        confirmed = self.env["delivery.time.booking"].search_count([
            ("slot_id", "=", slot.id),
            ("date", "=", self.date),
            ("state", "=", "confirmed"),
            ("id", "!=", self.id),
        ])
        if confirmed >= slot.capacity:
            return _(
                "The slot \"%(slot)s\" is full on %(date)s: %(count)s "
                "booking(s) already confirmed for a capacity of "
                "%(capacity)s.",
                slot=slot.name, date=self.date, count=confirmed,
                capacity=slot.capacity)
        return None

    @api.constrains("state", "date", "slot_id")
    def _check_availability(self):
        for booking in self:
            if booking.state != "confirmed":
                continue
            message = booking._availability_error()
            if message:
                raise ValidationError(message)

    def action_confirm(self):
        for booking in self:
            if booking.state != "draft":
                raise UserError(_(
                    "Only a draft booking can be confirmed."))
            message = booking._availability_error()
            if message:
                raise UserError(message)
            booking.state = "confirmed"
            booking.message_post(body=_(
                "Booking confirmed for %(date)s on %(slot)s.",
                date=booking.date, slot=booking.slot_id.name))
        return True

    def action_done(self):
        for booking in self:
            if booking.state != "confirmed":
                raise UserError(_(
                    "Only a confirmed booking can be marked as done."))
            booking.state = "done"
            booking.message_post(body=_(
                "Delivery unloaded and booking closed."))
        return True

    def action_cancel(self):
        for booking in self:
            if booking.state not in ("draft", "confirmed"):
                raise UserError(_(
                    "Only a draft or confirmed booking can be cancelled."))
            booking.state = "cancelled"
            booking.message_post(body=_(
                "Booking cancelled by %s.", self.env.user.name))
        return True

    def action_reset(self):
        for booking in self:
            if booking.state != "cancelled":
                raise UserError(_(
                    "Only a cancelled booking can be reset to draft."))
            booking.state = "draft"
            booking.message_post(body=_(
                "Booking reset to draft by %s.", self.env.user.name))
        return True


class DeliveryTimeBlackout(models.Model):
    _name = "delivery.time.blackout"
    _description = "Delivery Blackout Day"
    _order = "date desc, id desc"

    name = fields.Char(required=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today)
    slot_id = fields.Many2one(
        "delivery.time.slot", string="Time Slot", ondelete="cascade",
        help="Leave empty to close the whole day, whatever the slot.")
    reason = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    @api.constrains("date", "slot_id")
    def _check_duplicate(self):
        for blackout in self:
            duplicate = self.search_count([
                ("date", "=", blackout.date),
                ("slot_id", "=", blackout.slot_id.id or False),
                ("id", "!=", blackout.id),
            ])
            if duplicate:
                raise ValidationError(_(
                    "A blackout day already exists on %(date)s for "
                    "\"%(slot)s\".",
                    date=blackout.date,
                    slot=blackout.slot_id.name or _("the whole day")))
