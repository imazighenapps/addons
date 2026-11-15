# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SoftwareLicense(models.Model):
    _name = "software.license"
    _description = "Software License"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_expiry asc, id desc"

    name = fields.Char(string="Software / Product", required=True, tracking=True)
    vendor = fields.Char(string="Vendor", tracking=True)
    license_key = fields.Char(string="License Key / Reference")
    seats = fields.Integer(string="Seats", default=1)
    owner_id = fields.Many2one("res.users", string="Owner", tracking=True)
    date_purchase = fields.Date(string="Purchase Date")
    date_expiry = fields.Date(string="Expiry Date", tracking=True)
    is_expired = fields.Boolean(compute="_compute_expiry", string="Expired")
    state = fields.Selection(
        [("active", "Active"), ("expired", "Expired"), ("cancelled", "Cancelled")],
        default="active", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("date_expiry", "state")
    def _compute_expiry(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_expired = bool(
                rec.state == "active" and rec.date_expiry and rec.date_expiry < today)

    @api.constrains("seats")
    def _check_seats(self):
        for rec in self:
            if rec.seats < 0:
                raise ValidationError(_("Seats cannot be negative."))

    @api.constrains("date_purchase", "date_expiry")
    def _check_dates(self):
        for rec in self:
            if rec.date_purchase and rec.date_expiry and rec.date_expiry < rec.date_purchase:
                raise ValidationError(_("The expiry date cannot be before the purchase date."))

    def action_mark_expired(self):
        for rec in self:
            if rec.state == "cancelled":
                raise UserError(_("A cancelled license cannot be marked expired."))
            rec.state = "expired"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            rec.state = "active"
