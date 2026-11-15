# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HazardReportLog(models.Model):
    _name = "hazard.report.log"
    _description = "Hazard Report"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "report_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    report_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    reporter_id = fields.Many2one(
        "hr.employee", string="Reported By", tracking=True)
    location = fields.Char(tracking=True)
    hazard_type = fields.Selection(
        [("slip", "Slip / Trip / Fall"), ("electrical", "Electrical"),
         ("chemical", "Chemical"), ("ergonomic", "Ergonomic"),
         ("fire", "Fire"), ("other", "Other")],
        default="other", required=True, tracking=True)
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"),
         ("critical", "Critical")],
        default="medium", required=True, tracking=True)
    description = fields.Text(required=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    corrective_action = fields.Text()
    resolution_date = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("reported", "Reported"),
         ("progress", "In Progress"), ("resolved", "Resolved"),
         ("dismissed", "Dismissed")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("hazard.report.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    def action_report(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft report can be submitted."))
            record.state = "reported"
        return True

    def action_start(self):
        for record in self:
            if record.state != "reported":
                raise UserError(_("Only a reported hazard can be started."))
            record.state = "progress"
        return True

    def action_resolve(self):
        for record in self:
            if record.state != "progress":
                raise UserError(_("Only a hazard in progress can be resolved."))
            record.write({
                "state": "resolved",
                "resolution_date": fields.Date.context_today(record),
            })
        return True

    def action_dismiss(self):
        for record in self:
            if record.state not in ("reported", "progress"):
                raise UserError(_("Only a reported or in-progress hazard can be dismissed."))
            record.state = "dismissed"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state not in ("dismissed", "resolved"):
                raise UserError(_("Only a dismissed or resolved report can be reset to draft."))
            record.write({"state": "draft", "resolution_date": False})
        return True
