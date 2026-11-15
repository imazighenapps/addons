# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OnboardingChecklist(models.Model):
    _name = "onboarding.checklist"
    _description = "Onboarding Checklist"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, tracking=True)
    department_id = fields.Many2one(
        "hr.department", string="Department",
        related="employee_id.department_id", store=True, readonly=True)
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    date_start = fields.Date(
        string="Start Date", required=True, default=fields.Date.context_today, tracking=True)
    line_ids = fields.One2many(
        "onboarding.checklist.line", "checklist_id", string="Tasks", copy=True)
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"),
         ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("onboarding.checklist")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Onboarding Checklist",
                        "code": "onboarding.checklist",
                        "prefix": "ONB/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def _ensure_lines(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Add at least one task before continuing."))

    def action_start(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft checklist can be started."))
            rec._ensure_lines()
            rec.state = "in_progress"

    def action_done(self):
        for rec in self:
            if rec.state != "in_progress":
                raise UserError(_("Only an in-progress checklist can be completed."))
            rec.state = "done"

    def action_cancel(self):
        for rec in self:
            if rec.state in ("done", "cancelled"):
                raise UserError(_("This checklist cannot be cancelled."))
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            if rec.state != "cancelled":
                raise UserError(_("Only a cancelled checklist can be reset."))
            rec.state = "draft"


class OnboardingChecklistLine(models.Model):
    _name = "onboarding.checklist.line"
    _description = "Onboarding Checklist Line"
    _order = "checklist_id, sequence, id"

    checklist_id = fields.Many2one(
        "onboarding.checklist", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Task", required=True)
    user_id = fields.Many2one("res.users", string="Owner")
    date_due = fields.Date(string="Due Date")
    done = fields.Boolean(string="Done")
    note = fields.Char(string="Note")
    company_id = fields.Many2one(
        related="checklist_id.company_id", store=True, readonly=True)
