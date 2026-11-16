# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VehicleInspectionLog(models.Model):
    _name = "vehicle.inspection.log"
    _description = "Vehicle Inspection"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "inspection_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    vehicle_plate = fields.Char(
        string="Vehicle Plate", required=True, tracking=True)
    vehicle_model = fields.Char(string="Vehicle Model", tracking=True)
    inspection_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    odometer = fields.Integer(string="Odometer (km)", default=0)
    brake_ok = fields.Boolean(string="Brakes OK", default=True, tracking=True)
    tire_ok = fields.Boolean(string="Tyres OK", default=True, tracking=True)
    light_ok = fields.Boolean(string="Lights OK", default=True, tracking=True)
    body_ok = fields.Boolean(string="Body OK", default=True, tracking=True)
    inspector_id = fields.Many2one(
        "hr.employee", string="Inspector", tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("passed", "Passed"),
         ("defect", "Defect"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code(
                    "vehicle.inspection.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("odometer")
    def _check_odometer(self):
        for record in self:
            if record.odometer < 0:
                raise ValidationError(_("The odometer cannot be negative."))

    def action_pass(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft inspection can be passed."))
            if not (record.brake_ok and record.tire_ok
                    and record.light_ok and record.body_ok):
                raise UserError(
                    _("All checks must be OK before passing the inspection."))
            record.state = "passed"
        return True

    def action_flag_defect(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    _("Only a draft inspection can be flagged as a defect."))
            record.state = "defect"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("This inspection is already cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled inspection can be reset."))
            record.state = "draft"
        return True
