# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PettyExpenseLog(models.Model):
    _name = "petty.expense.log"
    _description = "Petty Expense"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expense_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    employee_id = fields.Many2one(
        "hr.employee", string="Requester", tracking=True)
    expense_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(required=True, currency_field="currency_id", tracking=True)
    category = fields.Char(string="Category")
    purpose = fields.Text()
    approver_id = fields.Many2one("res.users", string="Approver", tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("reimbursed", "Reimbursed"),
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
                seq = self.env["ir.sequence"].next_by_code("petty.expense.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("amount")
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_("The amount must be positive."))

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

    def action_reimburse(self):
        for record in self:
            if record.state != "approved":
                raise UserError(_("Only an approved request can be reimbursed."))
            record.state = "reimbursed"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state not in ("rejected", "reimbursed"):
                raise UserError(_("Only a rejected or reimbursed request can be reset to draft."))
            record.state = "draft"
        return True
