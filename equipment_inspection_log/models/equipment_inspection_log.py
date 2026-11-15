# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EquipmentInspectionLog(models.Model):
    _name = "equipment.inspection.log"
    _description = "Equipment Inspection"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "inspection_date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    equipment_id = fields.Many2one(
        "maintenance.equipment", string="Equipment", required=True, index=True, tracking=True)
    inspector_id = fields.Many2one(
        "hr.employee", string="Inspector", tracking=True, index=True)
    inspection_date = fields.Date(
        string="Inspection Date", required=True, default=fields.Date.context_today,
        tracking=True, index=True)
    condition = fields.Selection(
        [("good", "Good"), ("fair", "Fair"), ("poor", "Poor")],
        string="Condition", tracking=True)
    findings = fields.Text(string="Findings")
    followup_action = fields.Text(string="Follow-up Action")
    state = fields.Selection(
        [("planned", "Planned"), ("done", "Done"), ("issue_found", "Issue Found"),
         ("closed", "Closed")],
        default="planned", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("equipment.inspection.log")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Equipment Inspection",
                        "code": "equipment.inspection.log",
                        "prefix": "EIN/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_done(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError(_("Only a planned inspection can be marked done."))
            rec.state = "done"

    def action_issue(self):
        for rec in self:
            if rec.state not in ("planned", "done"):
                raise UserError(_("Only a planned or done inspection can be flagged with an issue."))
            rec.state = "issue_found"

    def action_close(self):
        for rec in self:
            if rec.state not in ("done", "issue_found"):
                raise UserError(_("Only a done or issue-found inspection can be closed."))
            rec.state = "closed"

    def action_reset(self):
        for rec in self:
            if rec.state == "planned":
                raise UserError(_("This inspection is already planned."))
            rec.state = "planned"
