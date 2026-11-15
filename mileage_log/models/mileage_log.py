# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class MileageLog(models.Model):
    _name = "mileage.log"
    _description = "Mileage Log Entry"
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
    origin = fields.Char(string="From")
    destination = fields.Char(string="To")
    purpose = fields.Char(string="Purpose", required=True, tracking=True)
    distance = fields.Float(string="Distance", required=True, tracking=True)
    rate = fields.Monetary(
        string="Rate", currency_field="currency_id", required=True, default=0.5)
    amount = fields.Monetary(
        compute="_compute_amount", currency_field="currency_id",
        string="Amount", store=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("validated", "Validated"), ("refused", "Refused")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("distance", "rate")
    def _compute_amount(self):
        for rec in self:
            rec.amount = (rec.distance or 0.0) * (rec.rate or 0.0)

    @api.constrains("distance", "rate")
    def _check_values(self):
        for rec in self:
            if rec.distance <= 0:
                raise ValidationError(_("Distance must be strictly positive."))
            if (rec.rate or 0.0) < -EPS:
                raise ValidationError(_("Rate cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("mileage.log")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Mileage Log",
                        "code": "mileage.log",
                        "prefix": "MIL/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft entry can be submitted."))
            rec.state = "submitted"

    def action_validate(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only a submitted entry can be validated."))
            rec.state = "validated"

    def action_refuse(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only a submitted entry can be refused."))
            rec.state = "refused"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
