# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ExitInterviewLog(models.Model):
    _name = "exit.interview.log"
    _description = "Exit Interview"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, tracking=True)
    department_id = fields.Many2one(
        "hr.department", string="Department",
        related="employee_id.department_id", store=True, readonly=True)
    interviewer_id = fields.Many2one(
        "res.users", string="Interviewer", default=lambda self: self.env.user,
        required=True, tracking=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    departure_reason = fields.Selection(
        [("career", "Career Opportunity"), ("compensation", "Compensation"),
         ("management", "Management"), ("personal", "Personal"),
         ("relocation", "Relocation"), ("other", "Other")],
        string="Primary Reason", default="other", required=True, tracking=True)
    feedback = fields.Text(string="Feedback")
    highlights = fields.Text(string="Highlights")
    concerns = fields.Text(string="Concerns")
    followup_action = fields.Text(string="Follow-up Actions")
    state = fields.Selection(
        [("draft", "Draft"), ("completed", "Completed"), ("reviewed", "Reviewed")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text(string="Confidential Notes")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("exit.interview.log")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Exit Interview",
                        "code": "exit.interview.log",
                        "prefix": "EXIT/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_complete(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft interview can be completed."))
            rec.state = "completed"

    def action_review(self):
        for rec in self:
            if rec.state != "completed":
                raise UserError(_("Only a completed interview can be reviewed."))
            rec.state = "reviewed"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
