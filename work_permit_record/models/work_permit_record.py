# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class WorkPermitRecord(models.Model):
    _name = "work.permit.record"
    _description = "Work Permit Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_expiry asc, id desc"

    name = fields.Char(string="Permit Title", required=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, tracking=True)
    department_id = fields.Many2one(
        "hr.department", string="Department",
        related="employee_id.department_id", store=True, readonly=True)
    permit_type = fields.Selection(
        [("work_permit", "Work Permit"), ("visa", "Visa"), ("authorization", "Authorization"),
         ("license", "License"), ("other", "Other")],
        string="Type", required=True, default="work_permit", tracking=True)
    reference = fields.Char(string="Reference / Number")
    issuer = fields.Char(string="Issuer / Authority")
    date_issue = fields.Date(string="Issue Date")
    date_expiry = fields.Date(string="Expiry Date", tracking=True)
    is_expired = fields.Boolean(compute="_compute_expiry", string="Expired")
    state = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired"), ("cancelled", "Cancelled")],
        default="valid", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("date_expiry", "state")
    def _compute_expiry(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_expired = bool(
                rec.state == "valid" and rec.date_expiry and rec.date_expiry < today)

    @api.constrains("date_issue", "date_expiry")
    def _check_dates(self):
        for rec in self:
            if rec.date_issue and rec.date_expiry and rec.date_expiry < rec.date_issue:
                raise ValidationError(_("The expiry date cannot be before the issue date."))

    def action_mark_expired(self):
        for rec in self:
            if rec.state == "cancelled":
                raise UserError(_("A cancelled permit cannot be marked expired."))
            rec.state = "expired"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            rec.state = "valid"
