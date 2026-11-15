# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DriverAssignmentLog(models.Model):
    _name = "driver.assignment.log"
    _description = "Driver Assignment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, index=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Driver (Employee)", required=True, index=True, tracking=True)
    date_start = fields.Date(
        string="Start Date", required=True, default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(string="End Date", tracking=True)
    reason = fields.Char(string="Reason / Notes")
    state = fields.Selection(
        [("active", "Active"), ("ended", "Ended"), ("cancelled", "Cancelled")],
        default="active", required=True, tracking=True, index=True)
    note = fields.Text(string="Details")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError(_("The end date cannot be before the start date."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("driver.assignment.log")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Driver Assignment",
                        "code": "driver.assignment.log",
                        "prefix": "DAS/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_end(self):
        for rec in self:
            if rec.state != "active":
                raise UserError(_("Only an active assignment can be ended."))
            rec.write({
                "state": "ended",
                "date_end": rec.date_end or fields.Date.context_today(rec),
            })

    def action_cancel(self):
        for rec in self:
            if rec.state == "cancelled":
                raise UserError(_("This assignment is already cancelled."))
            rec.state = "cancelled"

    def action_reactivate(self):
        for rec in self:
            if rec.state != "cancelled":
                raise UserError(_("Only a cancelled assignment can be reactivated."))
            rec.write({"state": "active", "date_end": False})
