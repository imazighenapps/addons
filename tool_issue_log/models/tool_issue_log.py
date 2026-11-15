# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ToolItem(models.Model):
    _name = "tool.item"
    _description = "Tool Item"
    _order = "name, id"

    name = fields.Char(string="Tool ID", required=True)
    category = fields.Char(string="Category")
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    _name_company_uniq = models.Constraint(
        "UNIQUE(name, company_id)",
        "A tool with this identifier already exists for this company.")


class ToolIssue(models.Model):
    _name = "tool.issue"
    _description = "Tool Issue Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_issue desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    tool_id = fields.Many2one(
        "tool.item", string="Tool", required=True, index=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, tracking=True)
    date_issue = fields.Date(
        string="Issue Date", required=True, default=fields.Date.context_today, tracking=True)
    date_return = fields.Date(string="Return Date", tracking=True)
    condition_out = fields.Char(string="Condition at Issue")
    condition_in = fields.Char(string="Condition at Return")
    state = fields.Selection(
        [("issued", "Issued"), ("returned", "Returned")],
        default="issued", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("date_issue", "date_return")
    def _check_dates(self):
        for rec in self:
            if rec.date_issue and rec.date_return and rec.date_return < rec.date_issue:
                raise ValidationError(_("The return date cannot be before the issue date."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("tool.issue")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Tool Issue",
                        "code": "tool.issue",
                        "prefix": "TOOL/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_return(self):
        for rec in self:
            if rec.state != "issued":
                raise UserError(_("Only an issued tool can be returned."))
            rec.write({
                "state": "returned",
                "date_return": rec.date_return or fields.Date.context_today(rec),
            })

    def action_reset(self):
        for rec in self:
            if rec.state != "returned":
                raise UserError(_("Only a returned issue can be reset."))
            rec.write({"state": "issued", "date_return": False})
