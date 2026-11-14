# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ParkingSpot(models.Model):
    _name = "parking.spot"
    _description = "Parking Spot"
    _order = "name, id"

    name = fields.Char(string="Spot", required=True)
    location = fields.Char(string="Location")
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    _name_company_uniq = models.Constraint(
        "UNIQUE(name, company_id)",
        "A parking spot with this name already exists for this company.")


class ParkingReservation(models.Model):
    _name = "parking.reservation"
    _description = "Parking Reservation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_datetime desc, id desc"

    name = fields.Char(
        string="Reference", compute="_compute_name", store=True)
    spot_id = fields.Many2one(
        "parking.spot", string="Spot", required=True, index=True, tracking=True)
    requester_id = fields.Many2one(
        "res.users", string="Requester", default=lambda self: self.env.user,
        required=True, tracking=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", tracking=True)
    vehicle_plate = fields.Char(string="Vehicle Plate")
    start_datetime = fields.Datetime(string="Start", required=True, tracking=True)
    stop_datetime = fields.Datetime(string="End", required=True, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("spot_id", "requester_id", "start_datetime")
    def _compute_name(self):
        for rec in self:
            parts = [p for p in [rec.spot_id.name, rec.requester_id.name] if p]
            rec.name = " / ".join(parts) if parts else _("Reservation")

    @api.constrains("start_datetime", "stop_datetime")
    def _check_dates(self):
        for rec in self:
            if rec.start_datetime and rec.stop_datetime and rec.stop_datetime <= rec.start_datetime:
                raise ValidationError(_("The end time must be after the start time."))

    @api.constrains("spot_id", "start_datetime", "stop_datetime", "state", "company_id")
    def _check_overlap(self):
        for rec in self:
            if rec.state != "confirmed" or not rec.spot_id:
                continue
            domain = [
                ("id", "!=", rec.id),
                ("spot_id", "=", rec.spot_id.id),
                ("state", "=", "confirmed"),
                ("start_datetime", "<", rec.stop_datetime),
                ("stop_datetime", ">", rec.start_datetime),
            ]
            if rec.company_id:
                domain.append(("company_id", "=", rec.company_id.id))
            other = self.search(domain, limit=1)
            if other:
                raise ValidationError(
                    _("Spot %(spot)s is already reserved during this time (%(ref)s).",
                      spot=rec.spot_id.display_name, ref=other.name))

    def action_confirm(self):
        for rec in self:
            if rec.state == "cancelled":
                raise UserError(_("A cancelled reservation cannot be confirmed."))
            rec.state = "confirmed"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
