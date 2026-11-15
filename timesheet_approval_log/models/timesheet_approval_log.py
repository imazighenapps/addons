# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TimesheetApprovalLog(models.Model):
    _name = "timesheet.approval.log"
    _description = "Timesheet Approval Log"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_end desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True,
        tracking=True)
    project_id = fields.Many2one(
        "project.project", string="Project", index=True, tracking=True)
    date_start = fields.Date(string="Period Start", required=True, tracking=True)
    date_end = fields.Date(string="Period End", required=True, tracking=True)
    total_hours = fields.Float(
        string="Total Hours", compute="_compute_total_hours", store=True)
    approver_id = fields.Many2one(
        "res.users", string="Approver", tracking=True)
    submitted_date = fields.Date(readonly=True, copy=False)
    approved_date = fields.Date(readonly=True, copy=False)
    reject_reason = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("rejected", "Rejected")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code(
                    "timesheet.approval.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.depends("employee_id", "date_start", "date_end", "project_id")
    def _compute_total_hours(self):
        Analytic = self.env["account.analytic.line"]
        for record in self:
            if not (record.employee_id and record.date_start and record.date_end):
                record.total_hours = 0.0
                continue
            domain = [
                ("employee_id", "=", record.employee_id.id),
                ("date", ">=", record.date_start),
                ("date", "<=", record.date_end),
            ]
            if record.project_id:
                domain.append(("project_id", "=", record.project_id.id))
            lines = Analytic.search(domain)
            record.total_hours = sum(lines.mapped("unit_amount"))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for record in self:
            if record.date_end < record.date_start:
                raise ValidationError(
                    _("The period end date cannot be before the start date."))

    def action_submit(self):
        for record in self:
            if record.state not in ("draft", "rejected"):
                raise UserError(_("Only a draft or rejected log can be submitted."))
            record.write({
                "state": "submitted",
                "submitted_date": fields.Date.context_today(record),
            })
        return True

    def action_approve(self):
        for record in self:
            if record.state != "submitted":
                raise UserError(_("Only a submitted log can be approved."))
            record.write({
                "state": "approved",
                "approver_id": self.env.user.id,
                "approved_date": fields.Date.context_today(record),
            })
        return True

    def action_reject(self):
        for record in self:
            if record.state != "submitted":
                raise UserError(_("Only a submitted log can be rejected."))
            record.write({
                "state": "rejected",
                "approver_id": self.env.user.id,
            })
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state not in ("rejected", "submitted"):
                raise UserError(_("Only a rejected or submitted log can be reset to draft."))
            record.write({
                "state": "draft",
                "submitted_date": False,
                "approved_date": False,
                "approver_id": False,
            })
        return True
