# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ToolCalibrationLog(models.Model):
    _name = "tool.calibration.log"
    _description = "Tool Calibration"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "calibration_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    equipment_id = fields.Many2one(
        "maintenance.equipment", string="Tool / Equipment", required=True,
        index=True, tracking=True)
    calibration_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    next_due_date = fields.Date(string="Next Due Date", tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Provider", tracking=True)
    certificate_ref = fields.Char(string="Certificate Reference")
    result = fields.Selection(
        [("pass", "Pass"), ("fail", "Fail"), ("adjusted", "Adjusted")],
        tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    note = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("scheduled", "Scheduled"),
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
                seq = self.env["ir.sequence"].next_by_code("tool.calibration.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("calibration_date", "next_due_date")
    def _check_dates(self):
        for record in self:
            if record.next_due_date and record.calibration_date \
                    and record.next_due_date < record.calibration_date:
                raise ValidationError(
                    _("The next due date cannot be before the calibration date."))

    def action_schedule(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft calibration can be scheduled."))
            record.state = "scheduled"
        return True

    def action_done(self):
        for record in self:
            if record.state != "scheduled":
                raise UserError(_("Only a scheduled calibration can be marked done."))
            record.state = "done"
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("done", "cancelled"):
                raise UserError(_("A done or cancelled calibration cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled calibration can be reset to draft."))
            record.state = "draft"
        return True
