# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DockAppointmentLog(models.Model):
    _name = "dock.appointment.log"
    _description = "Dock Appointment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "appointment_date asc, id asc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    appointment_date = fields.Datetime(
        required=True, default=fields.Datetime.now, tracking=True)
    dock_name = fields.Char(string="Dock", required=True, tracking=True)
    direction = fields.Selection(
        [("in", "Inbound"), ("out", "Outbound")],
        required=True, default="in", tracking=True)
    carrier_name = fields.Char(string="Carrier", tracking=True)
    vehicle_plate = fields.Char(string="Vehicle Plate")
    reference = fields.Char(string="Shipment / Order Reference")
    pallet_count = fields.Integer(default=0)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"),
         ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("dock.appointment.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("pallet_count")
    def _check_pallet_count(self):
        for record in self:
            if record.pallet_count < 0:
                raise ValidationError(_("Pallet count cannot be negative."))

    def action_confirm(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft appointment can be confirmed."))
            record.state = "confirmed"
        return True

    def action_done(self):
        for record in self:
            if record.state != "confirmed":
                raise UserError(_("Only a confirmed appointment can be closed."))
            record.state = "done"
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("done", "cancelled"):
                raise UserError(_("A done or cancelled appointment cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled appointment can be reset."))
            record.state = "draft"
        return True
