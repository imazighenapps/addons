# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class NoiseExposureLog(models.Model):
    _name = "noise.exposure.log"
    _description = "Noise Exposure Measurement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "measurement_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    location = fields.Char(
        string="Area", required=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", tracking=True)
    measurement_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    measured_db = fields.Float(string="Measured Level (dB)", required=True)
    limit_db = fields.Float(string="Limit (dB)", default=85.0, required=True)
    exposure_minutes = fields.Integer(default=60, required=True)
    exceeds_limit = fields.Boolean(
        string="Exceeds Limit", compute="_compute_exceeds_limit", store=True)
    user_id = fields.Many2one(
        "res.users", string="Measured By", default=lambda self: self.env.user,
        tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("recorded", "Recorded"),
         ("action_required", "Action Required"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.depends("measured_db", "limit_db")
    def _compute_exceeds_limit(self):
        for record in self:
            record.exceeds_limit = record.measured_db > record.limit_db

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("noise.exposure.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("measured_db", "limit_db", "exposure_minutes")
    def _check_values(self):
        for record in self:
            if record.measured_db < 0:
                raise ValidationError(_("The measured level cannot be negative."))
            if record.limit_db <= 0:
                raise ValidationError(_("The limit must be positive."))
            if record.exposure_minutes <= 0:
                raise ValidationError(_("Exposure duration must be positive."))

    def action_record(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft measurement can be recorded."))
            record.state = "action_required" if record.exceeds_limit else "recorded"
        return True

    def action_resolve(self):
        for record in self:
            if record.state != "action_required":
                raise UserError(
                    _("Only an action-required measurement can be resolved."))
            record.state = "recorded"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("This measurement is already cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled measurement can be reset."))
            record.state = "draft"
        return True
