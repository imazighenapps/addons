# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class FleetTireLog(models.Model):
    _name = "fleet.tire.log"
    _description = "Fleet Tire Event"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "event_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    vehicle_plate = fields.Char(
        string="Vehicle Plate", required=True, tracking=True)
    tire_brand = fields.Char(string="Tire Brand", tracking=True)
    position = fields.Selection(
        [("fl", "Front Left"), ("fr", "Front Right"), ("rl", "Rear Left"),
         ("rr", "Rear Right"), ("spare", "Spare")],
        required=True, default="fl", tracking=True)
    event_type = fields.Selection(
        [("fitting", "Fitting"), ("rotation", "Rotation"),
         ("replacement", "Replacement"), ("removal", "Removal")],
        required=True, default="rotation", tracking=True)
    event_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    tread_depth_mm = fields.Float(string="Tread Depth (mm)", default=8.0)
    odometer = fields.Integer(string="Odometer (km)", default=0)
    unit_cost = fields.Float(string="Unit Cost")
    technician_id = fields.Many2one(
        "hr.employee", string="Technician", tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("recorded", "Recorded"),
         ("due", "Due"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("fleet.tire.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("tread_depth_mm", "odometer", "unit_cost")
    def _check_values(self):
        for record in self:
            if record.tread_depth_mm < 0 or record.tread_depth_mm > 25:
                raise ValidationError(
                    _("The tread depth must be between 0 and 25 mm."))
            if record.odometer < 0:
                raise ValidationError(_("The odometer cannot be negative."))
            if record.unit_cost < 0:
                raise ValidationError(_("The unit cost cannot be negative."))

    def action_record(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft tire event can be recorded."))
            record.state = "recorded"
        return True

    def action_mark_due(self):
        for record in self:
            if record.state != "recorded":
                raise UserError(_("Only a recorded tire event can be due."))
            record.state = "due"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("This tire event is already cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled tire event can be reset."))
            record.state = "draft"
        return True
