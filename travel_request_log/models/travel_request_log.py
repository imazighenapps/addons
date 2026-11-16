# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TravelRequestLog(models.Model):
    _name = "travel.request.log"
    _description = "Travel Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, tracking=True)
    destination = fields.Char(required=True, tracking=True)
    date_start = fields.Date(string="Start Date", required=True, tracking=True)
    date_end = fields.Date(string="End Date", required=True, tracking=True)
    purpose = fields.Text(required=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    estimated_cost = fields.Monetary(currency_field="currency_id", tracking=True)
    approver_id = fields.Many2one("res.users", string="Approver", tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    note = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("completed", "Completed"),
         ("rejected", "Rejected")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("travel.request.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end and record.date_end < record.date_start:
                raise ValidationError(_("The end date cannot be before the start date."))

    def action_submit(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft request can be submitted."))
            record.state = "submitted"
        return True

    def action_approve(self):
        for record in self:
            if record.state != "submitted":
                raise UserError(_("Only a submitted request can be approved."))
            record.write({"state": "approved", "approver_id": self.env.user.id})
        return True

    def action_reject(self):
        for record in self:
            if record.state != "submitted":
                raise UserError(_("Only a submitted request can be rejected."))
            record.state = "rejected"
        return True

    def action_complete(self):
        for record in self:
            if record.state != "approved":
                raise UserError(_("Only an approved request can be completed."))
            record.state = "completed"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state not in ("rejected", "completed"):
                raise UserError(_("Only a rejected or completed request can be reset to draft."))
            record.state = "draft"
        return True
