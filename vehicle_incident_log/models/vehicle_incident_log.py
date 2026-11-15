# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VehicleIncidentLog(models.Model):
    _name = "vehicle.incident.log"
    _description = "Vehicle Incident"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, index=True, tracking=True)
    driver_id = fields.Many2one(
        "res.partner", string="Driver", tracking=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", tracking=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    location = fields.Char(string="Location", required=True, tracking=True)
    description = fields.Text(string="Description", required=True)
    damage = fields.Text(string="Damage Details")
    third_party = fields.Char(string="Third Party Involved")
    insurance_ref = fields.Char(string="Insurance Reference")
    followup_action = fields.Text(string="Follow-up Actions")
    state = fields.Selection(
        [("draft", "Draft"), ("reported", "Reported"), ("in_progress", "In Progress"),
         ("closed", "Closed")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("vehicle.incident.log")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Vehicle Incident",
                        "code": "vehicle.incident.log",
                        "prefix": "VIN/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_report(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft incident can be reported."))
            rec.state = "reported"

    def action_start(self):
        for rec in self:
            if rec.state != "reported":
                raise UserError(_("Only a reported incident can be moved in progress."))
            rec.state = "in_progress"

    def action_close(self):
        for rec in self:
            if rec.state not in ("reported", "in_progress"):
                raise UserError(_("Only a reported or in-progress incident can be closed."))
            rec.state = "closed"

    def action_reset(self):
        for rec in self:
            if rec.state != "closed":
                raise UserError(_("Only a closed incident can be reset."))
            rec.state = "draft"
