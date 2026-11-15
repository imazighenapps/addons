# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ItAccessRequest(models.Model):
    _name = "it.access.request"
    _description = "IT Access Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_request desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    requester_id = fields.Many2one(
        "res.users", string="Requester", default=lambda self: self.env.user,
        required=True, tracking=True, index=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", tracking=True)
    department_id = fields.Many2one(
        "hr.department", string="Department",
        related="employee_id.department_id", store=True, readonly=True)
    system_name = fields.Char(string="System / Resource", required=True, tracking=True)
    access_type = fields.Selection(
        [("read", "Read"), ("write", "Read/Write"), ("admin", "Admin"), ("other", "Other")],
        default="read", required=True, string="Access Type", tracking=True)
    justification = fields.Text(string="Justification", required=True)
    date_request = fields.Date(
        string="Request Date", required=True,
        default=fields.Date.context_today, tracking=True)
    date_needed = fields.Date(string="Needed By")
    date_granted = fields.Date(string="Granted On")
    date_revoked = fields.Date(string="Revoked On")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"),
         ("refused", "Refused"), ("granted", "Granted"), ("revoked", "Revoked")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text(string="Reviewer Notes")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("it.access.request")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "IT Access Request",
                        "code": "it.access.request",
                        "prefix": "ACC/%(year)s/",
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

    def action_grant(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError(_("Only an approved request can be granted."))
            rec.write({
                "state": "granted",
                "date_granted": rec.date_granted or fields.Date.context_today(rec),
                "date_revoked": False,
            })

    def action_revoke(self):
        for rec in self:
            if rec.state != "granted":
                raise UserError(_("Only a granted request can be revoked."))
            rec.write({
                "state": "revoked",
                "date_revoked": rec.date_revoked or fields.Date.context_today(rec),
            })

    def action_reset(self):
        for rec in self:
            if rec.state in ("draft", "submitted"):
                raise UserError(_("This request can already be edited."))
            rec.state = "draft"
