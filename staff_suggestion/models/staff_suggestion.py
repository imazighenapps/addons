# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StaffSuggestion(models.Model):
    _name = "staff.suggestion"
    _description = "Staff Suggestion"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Title", required=True, tracking=True)
    submitter_id = fields.Many2one(
        "res.users", string="Submitted By", default=lambda self: self.env.user,
        required=True, tracking=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", tracking=True)
    department_id = fields.Many2one(
        "hr.department", string="Department",
        related="employee_id.department_id", store=True, readonly=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    category = fields.Selection(
        [("process", "Process"), ("safety", "Safety"), ("quality", "Quality"),
         ("cost", "Cost Saving"), ("other", "Other")],
        default="other", required=True, tracking=True)
    description = fields.Text(string="Description", required=True)
    expected_benefit = fields.Text(string="Expected Benefit")
    reviewer_note = fields.Text(string="Reviewer Notes")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("under_review", "Under Review"),
         ("accepted", "Accepted"), ("rejected", "Rejected"), ("done", "Done")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft suggestion can be submitted."))
            rec.state = "submitted"

    def action_review(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only a submitted suggestion can be moved to review."))
            rec.state = "under_review"

    def action_accept(self):
        for rec in self:
            if rec.state != "under_review":
                raise UserError(_("Only a suggestion under review can be accepted."))
            rec.state = "accepted"

    def action_reject(self):
        for rec in self:
            if rec.state != "under_review":
                raise UserError(_("Only a suggestion under review can be rejected."))
            rec.state = "rejected"

    def action_done(self):
        for rec in self:
            if rec.state != "accepted":
                raise UserError(_("Only an accepted suggestion can be marked done."))
            rec.state = "done"

    def action_reset(self):
        for rec in self:
            if rec.state in ("draft", "submitted"):
                raise UserError(_("This suggestion can already be edited."))
            rec.state = "draft"
