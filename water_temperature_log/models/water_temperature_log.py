# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class WaterTemperatureLog(models.Model):
    _name = "water.temperature.log"
    _description = "Water Temperature Reading"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "reading_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    point_name = fields.Char(
        string="Point", required=True, tracking=True)
    point_type = fields.Selection(
        [("tap", "Tap"), ("shower", "Shower"), ("tank", "Tank"),
         ("boiler", "Boiler"), ("other", "Other")],
        required=True, default="tap", tracking=True)
    reading_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    temperature_c = fields.Float(
        string="Temperature (C)", required=True)
    target_min_c = fields.Float(string="Target Min (C)", default=50.0)
    target_max_c = fields.Float(string="Target Max (C)", default=65.0)
    within_range = fields.Boolean(
        string="Within Range", compute="_compute_within_range", store=True)
    reader_id = fields.Many2one(
        "hr.employee", string="Read By", tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("recorded", "Recorded"),
         ("alert", "Alert"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.depends("temperature_c", "target_min_c", "target_max_c")
    def _compute_within_range(self):
        for record in self:
            record.within_range = (
                record.target_min_c <= record.temperature_c <= record.target_max_c)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code(
                    "water.temperature.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("temperature_c")
    def _check_temperature(self):
        for record in self:
            if record.temperature_c < -10 or record.temperature_c > 120:
                raise ValidationError(
                    _("Temperature must be between -10 and 120 C."))

    @api.constrains("target_min_c", "target_max_c")
    def _check_targets(self):
        for record in self:
            if record.target_min_c >= record.target_max_c:
                raise ValidationError(
                    _("The target minimum must be below the target maximum."))

    def action_record(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft reading can be recorded."))
            record.state = "recorded" if record.within_range else "alert"
        return True

    def action_resolve(self):
        for record in self:
            if record.state != "alert":
                raise UserError(_("Only an alert reading can be resolved."))
            record.state = "recorded"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("This reading is already cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled reading can be reset."))
            record.state = "draft"
        return True
