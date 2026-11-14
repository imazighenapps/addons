# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class BookingVehicle(models.Model):
    _name = "booking.vehicle"
    _description = "Booking Vehicle"
    _order = "name, id"

    name = fields.Char(required=True)
    plate = fields.Char(string="Plate / Reference")
    seats = fields.Integer(string="Seats")
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    _name_company_uniq = models.Constraint(
        "UNIQUE(name, company_id)",
        "A vehicle with this name already exists for this company.")


class VehicleBooking(models.Model):
    _name = "vehicle.booking"
    _description = "Vehicle Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_datetime desc, id desc"

    name = fields.Char(string="Purpose", required=True, tracking=True)
    vehicle_id = fields.Many2one(
        "booking.vehicle", string="Vehicle", required=True, index=True, tracking=True)
    requester_id = fields.Many2one(
        "res.users", string="Requester", default=lambda self: self.env.user,
        required=True, tracking=True)
    employee_id = fields.Many2one("hr.employee", string="Driver / Employee", tracking=True)
    start_datetime = fields.Datetime(string="Start", required=True, tracking=True)
    stop_datetime = fields.Datetime(string="End", required=True, tracking=True)
    destination = fields.Char(string="Destination")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("start_datetime", "stop_datetime")
    def _check_dates(self):
        for rec in self:
            if rec.start_datetime and rec.stop_datetime and rec.stop_datetime <= rec.start_datetime:
                raise ValidationError(_("The end time must be after the start time."))

    @api.constrains("vehicle_id", "start_datetime", "stop_datetime", "state", "company_id")
    def _check_overlap(self):
        for rec in self:
            if rec.state not in ("confirmed", "done") or not rec.vehicle_id:
                continue
            domain = [
                ("id", "!=", rec.id),
                ("vehicle_id", "=", rec.vehicle_id.id),
                ("state", "in", ("confirmed", "done")),
                ("start_datetime", "<", rec.stop_datetime),
                ("stop_datetime", ">", rec.start_datetime),
            ]
            if rec.company_id:
                domain.append(("company_id", "=", rec.company_id.id))
            other = self.search(domain, limit=1)
            if other:
                raise ValidationError(
                    _("Vehicle %(vehicle)s is already booked during this time (%(name)s).",
                      vehicle=rec.vehicle_id.display_name, name=other.name))

    def action_confirm(self):
        for rec in self:
            if rec.state == "cancelled":
                raise UserError(_("A cancelled booking cannot be confirmed."))
            rec.state = "confirmed"

    def action_done(self):
        for rec in self:
            if rec.state != "confirmed":
                raise UserError(_("Only a confirmed booking can be marked done."))
            rec.state = "done"

    def action_cancel(self):
        for rec in self:
            if rec.state == "done":
                raise UserError(_("A completed booking cannot be cancelled."))
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            if rec.state != "cancelled":
                raise UserError(_("Only a cancelled booking can be reset."))
            rec.state = "draft"
