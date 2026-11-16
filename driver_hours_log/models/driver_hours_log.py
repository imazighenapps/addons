# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DriverHoursLog(models.Model):
    _name = "driver.hours.log"
    _description = "Driver Duty Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "duty_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    employee_id = fields.Many2one(
        "hr.employee", string="Driver", required=True, index=True,
        tracking=True)
    vehicle_plate = fields.Char(string="Vehicle Plate", tracking=True)
    duty_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    driving_minutes = fields.Integer(
        string="Driving (minutes)", required=True, default=0)
    break_minutes = fields.Integer(
        string="Break (minutes)", default=0)
    limit_minutes = fields.Integer(
        string="Daily Limit (minutes)", default=540, required=True)
    exceeds_limit = fields.Boolean(
        string="Exceeds Limit", compute="_compute_exceeds_limit", store=True)
    user_id = fields.Many2one(
        "res.users", string="Recorded By", default=lambda self: self.env.user,
        tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("validated", "Validated"),
         ("alert", "Alert"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.depends("driving_minutes", "limit_minutes")
    def _compute_exceeds_limit(self):
        for record in self:
            record.exceeds_limit = record.driving_minutes > record.limit_minutes

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("driver.hours.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("driving_minutes", "break_minutes", "limit_minutes")
    def _check_minutes(self):
        for record in self:
            if record.driving_minutes <= 0 or record.driving_minutes > 1440:
                raise ValidationError(
                    _("Driving minutes must be between 1 and 1440."))
            if record.break_minutes < 0 or record.break_minutes > 1440:
                raise ValidationError(
                    _("Break minutes must be between 0 and 1440."))
            if record.limit_minutes <= 0 or record.limit_minutes > 1440:
                raise ValidationError(
                    _("The daily limit must be between 1 and 1440 minutes."))

    def action_validate(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft duty record can be validated."))
            record.state = "alert" if record.exceeds_limit else "validated"
        return True

    def action_resolve(self):
        for record in self:
            if record.state != "alert":
                raise UserError(_("Only an alert duty record can be resolved."))
            record.state = "validated"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("This duty record is already cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled duty record can be reset."))
            record.state = "draft"
        return True
