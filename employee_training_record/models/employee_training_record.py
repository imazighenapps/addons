# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TrainingType(models.Model):
    _name = "employee.training.type"
    _description = "Training Type"
    _order = "name, id"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    validity_days = fields.Integer(
        string="Default Validity (days)",
        help="Default number of days the training remains valid. 0 means no expiry.")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_company_uniq', "UNIQUE(name, company_id)", "A training type with this name already exists for this company."),
    ]


class EmployeeTrainingRecord(models.Model):
    _name = "employee.training.record"
    _description = "Employee Training Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_done desc, id desc"

    name = fields.Char(
        string="Training Title", required=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True,
        tracking=True)
    department_id = fields.Many2one(
        "hr.department", string="Department",
        related="employee_id.department_id", store=True, readonly=True)
    type_id = fields.Many2one(
        "employee.training.type", string="Training Type", tracking=True)
    provider = fields.Char(string="Provider")
    date_done = fields.Date(
        string="Completion Date", required=True,
        default=fields.Date.context_today, tracking=True)
    date_expiry = fields.Date(string="Expiry Date", tracking=True)
    certificate_ref = fields.Char(string="Certificate Reference")
    duration_hours = fields.Float(string="Duration (hours)")
    cost = fields.Monetary(string="Cost", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    status = fields.Selection(
        [("valid", "Valid"), ("expiring", "Expiring Soon"),
         ("expired", "Expired"), ("no_expiry", "No Expiry")],
        compute="_compute_status", store=True, string="Status")
    state = fields.Selection(
        [("planned", "Planned"), ("done", "Done"), ("cancelled", "Cancelled")],
        default="done", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("date_expiry", "state")
    def _compute_status(self):
        today = fields.Date.context_today(self)
        soon = today + timedelta(days=30)
        for rec in self:
            if rec.state == "cancelled":
                rec.status = "no_expiry"
                continue
            if not rec.date_expiry:
                rec.status = "no_expiry"
            elif rec.date_expiry < today:
                rec.status = "expired"
            elif rec.date_expiry <= soon:
                rec.status = "expiring"
            else:
                rec.status = "valid"

    @api.onchange("type_id", "date_done")
    def _onchange_type_dates(self):
        if self.type_id and self.type_id.validity_days and self.date_done and not self.date_expiry:
            self.date_expiry = self.date_done + timedelta(days=self.type_id.validity_days)

    @api.constrains("date_done", "date_expiry")
    def _check_dates(self):
        for rec in self:
            if rec.date_expiry and rec.date_done and rec.date_expiry < rec.date_done:
                raise ValidationError(
                    _("The expiry date cannot be before the completion date."))

    def action_done(self):
        for rec in self:
            rec.state = "done"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            rec.state = "planned"
