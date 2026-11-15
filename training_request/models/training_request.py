# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class TrainingRequest(models.Model):
    _name = "training.request"
    _description = "Training Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_request desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, tracking=True)
    department_id = fields.Many2one(
        "hr.department", string="Department",
        related="employee_id.department_id", store=True, readonly=True)
    topic = fields.Char(string="Training Topic", required=True, tracking=True)
    provider = fields.Char(string="Provider")
    date_request = fields.Date(
        string="Request Date", required=True,
        default=fields.Date.context_today, tracking=True)
    date_start = fields.Date(string="Requested Start")
    date_end = fields.Date(string="Requested End")
    estimated_cost = fields.Monetary(
        string="Estimated Cost", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    justification = fields.Text(string="Justification")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"),
         ("refused", "Refused"), ("done", "Done")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text(string="Reviewer Notes")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError(_("The end date cannot be before the start date."))

    @api.constrains("estimated_cost")
    def _check_cost(self):
        for rec in self:
            if (rec.estimated_cost or 0.0) < -EPS:
                raise ValidationError(_("Estimated cost cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("training.request")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Training Request",
                        "code": "training.request",
                        "prefix": "TR/%(year)s/",
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

    def action_done(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError(_("Only an approved request can be marked done."))
            rec.state = "done"

    def action_reset(self):
        for rec in self:
            if rec.state in ("draft", "submitted"):
                raise UserError(_("This request can already be edited."))
            rec.state = "draft"
