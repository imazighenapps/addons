# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CoolerTemperatureLog(models.Model):
    _name = "cooler.temperature.log"
    _description = "Cold Storage Temperature Reading"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "reading_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    cooler_name = fields.Char(
        string="Cooler", required=True, tracking=True)
    location = fields.Char(tracking=True)
    reading_date = fields.Datetime(
        required=True, default=fields.Datetime.now, tracking=True)
    temperature_c = fields.Float(
        string="Temperature (C)", required=True)
    target_min_c = fields.Float(string="Target Min (C)", default=0.0)
    target_max_c = fields.Float(string="Target Max (C)", default=4.0)
    within_range = fields.Boolean(
        string="Within Range", compute="_compute_within_range", store=True)
    reader_id = fields.Many2one(
        "hr.employee", string="Read By", tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("recorded", "Recorded"),
         ("breach", "Breach"), ("cancelled", "Cancelled")],
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
                    "cooler.temperature.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("temperature_c")
    def _check_temperature(self):
        for record in self:
            if record.temperature_c < -50 or record.temperature_c > 40:
                raise ValidationError(
                    _("Temperature must be between -50 and 40 C."))

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
            record.state = "recorded" if record.within_range else "breach"
        return True

    def action_resolve(self):
        for record in self:
            if record.state != "breach":
                raise UserError(_("Only a breach reading can be resolved."))
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
