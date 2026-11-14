# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EmployeeOvertime(models.Model):
    _name = "employee.overtime"
    _description = "Employee Overtime Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, tracking=True)
    department_id = fields.Many2one(
        "hr.department", string="Department",
        related="employee_id.department_id", store=True, readonly=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    hours = fields.Float(string="Hours", required=True, tracking=True)
    overtime_type = fields.Selection(
        [("weekday", "Weekday"), ("weekend", "Weekend"), ("holiday", "Holiday"),
         ("other", "Other")],
        default="weekday", string="Type", tracking=True)
    reason = fields.Text(string="Reason")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("refused", "Refused")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("hours")
    def _check_hours(self):
        for rec in self:
            if rec.hours <= 0:
                raise ValidationError(_("Overtime hours must be strictly positive."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("employee.overtime")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Employee Overtime",
                        "code": "employee.overtime",
                        "prefix": "OT/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft request can be submitted."))
            rec.state = "submitted"

    def action_approve(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only a submitted request can be approved."))
            rec.state = "approved"

    def action_refuse(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only a submitted request can be refused."))
            rec.state = "refused"

    def action_reset(self):
        for rec in self:
            if rec.state not in ("refused", "approved"):
                raise UserError(_("Only an approved or refused request can be reset."))
            rec.state = "draft"
