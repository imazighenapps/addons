# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ShiftHandoverLog(models.Model):
    _name = "shift.handover.log"
    _description = "Shift Handover Log"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    shift = fields.Selection(
        [("morning", "Morning"), ("afternoon", "Afternoon"), ("night", "Night"),
         ("other", "Other")],
        default="morning", required=True, tracking=True)
    area = fields.Char(string="Area / Line", required=True, tracking=True)
    outgoing_id = fields.Many2one(
        "hr.employee", string="Outgoing Responsible", tracking=True)
    incoming_id = fields.Many2one(
        "hr.employee", string="Incoming Responsible", tracking=True)
    summary = fields.Text(string="Status Summary", required=True)
    incidents = fields.Text(string="Incidents / Issues")
    pending_tasks = fields.Text(string="Pending Tasks")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("acknowledged", "Acknowledged")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("shift.handover.log")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Shift Handover",
                        "code": "shift.handover.log",
                        "prefix": "SH/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft handover can be submitted."))
            rec.state = "submitted"

    def action_acknowledge(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only a submitted handover can be acknowledged."))
            rec.state = "acknowledged"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
