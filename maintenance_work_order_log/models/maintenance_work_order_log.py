# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MaintenanceWorkOrderLog(models.Model):
    _name = "maintenance.work.order.log"
    _description = "Maintenance Work Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_planned desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    equipment_id = fields.Many2one(
        "maintenance.equipment", string="Equipment", required=True,
        index=True, tracking=True)
    request_id = fields.Many2one(
        "maintenance.request", string="Maintenance Request", index=True,
        tracking=True)
    technician_id = fields.Many2one(
        "hr.employee", string="Technician", tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    date_planned = fields.Date(
        string="Planned Date", default=fields.Date.context_today, tracking=True)
    date_start = fields.Datetime(string="Start")
    date_end = fields.Datetime(string="End")
    duration = fields.Float(
        string="Duration (hours)", compute="_compute_duration", store=True)
    description = fields.Text(string="Work Description")
    parts_note = fields.Text(string="Parts / Consumables")
    outcome = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("progress", "In Progress"),
         ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code(
                    "maintenance.work.order.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.depends("date_start", "date_end")
    def _compute_duration(self):
        for record in self:
            if record.date_start and record.date_end:
                delta = record.date_end - record.date_start
                record.duration = max(delta.total_seconds() / 3600.0, 0.0)
            else:
                record.duration = 0.0

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end \
                    and record.date_end < record.date_start:
                raise ValidationError(
                    _("The end date cannot be before the start date."))

    def action_start(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft work order can be started."))
            values = {"state": "progress"}
            if not record.date_start:
                values["date_start"] = fields.Datetime.now()
            record.write(values)
        return True

    def action_done(self):
        for record in self:
            if record.state != "progress":
                raise UserError(_("Only a work order in progress can be completed."))
            values = {"state": "done"}
            if not record.date_end:
                values["date_end"] = fields.Datetime.now()
            record.write(values)
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("done", "cancelled"):
                raise UserError(_("A done or cancelled work order cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled work order can be reset to draft."))
            record.write({"state": "draft", "date_start": False, "date_end": False})
        return True
