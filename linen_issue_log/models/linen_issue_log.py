# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LinenIssueLog(models.Model):
    _name = "linen.issue.log"
    _description = "Linen Issue"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "issue_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    item_name = fields.Char(string="Item / Description", required=True, tracking=True)
    quantity = fields.Integer(default=1, required=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Department / Contact", tracking=True)
    issue_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    expected_return_date = fields.Date(tracking=True)
    return_date = fields.Date()
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    condition_note = fields.Text(string="Condition / Notes")
    state = fields.Selection(
        [("draft", "Draft"), ("issued", "Issued"),
         ("returned", "Returned"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("linen.issue.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_("Quantity must be positive."))

    @api.constrains("issue_date", "expected_return_date", "return_date")
    def _check_dates(self):
        for record in self:
            if record.expected_return_date and record.issue_date \
                    and record.expected_return_date < record.issue_date:
                raise ValidationError(
                    _("The expected return date cannot be before the issue date."))
            if record.return_date and record.issue_date \
                    and record.return_date < record.issue_date:
                raise ValidationError(
                    _("The return date cannot be before the issue date."))

    def action_issue(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft record can be issued."))
            record.state = "issued"
        return True

    def action_return(self):
        for record in self:
            if record.state != "issued":
                raise UserError(_("Only an issued record can be marked returned."))
            record.write({
                "state": "returned",
                "return_date": record.return_date or fields.Date.context_today(record),
            })
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("returned", "cancelled"):
                raise UserError(_("A returned or cancelled record cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled record can be reset to draft."))
            record.write({"state": "draft", "return_date": False})
        return True
