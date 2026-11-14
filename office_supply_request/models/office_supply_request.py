# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class OfficeSupplyRequest(models.Model):
    _name = "office.supply.request"
    _description = "Office Supply Request"
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
    date_request = fields.Date(
        string="Request Date", required=True,
        default=fields.Date.context_today, tracking=True)
    date_needed = fields.Date(string="Needed By", tracking=True)
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Urgent")], default="0", tracking=True)
    line_ids = fields.One2many(
        "office.supply.request.line", "request_id", string="Lines", copy=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"),
         ("fulfilled", "Fulfilled"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text(string="Notes")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("office.supply.request")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Office Supply Request",
                        "code": "office.supply.request",
                        "prefix": "OSR/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def _ensure_lines(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Add at least one line before continuing."))

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft request can be submitted."))
            rec._ensure_lines()
            rec.state = "submitted"

    def action_approve(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only a submitted request can be approved."))
            rec._ensure_lines()
            rec.state = "approved"

    def action_fulfill(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError(_("Only an approved request can be fulfilled."))
            rec.state = "fulfilled"

    def action_cancel(self):
        for rec in self:
            if rec.state in ("fulfilled", "cancelled"):
                raise UserError(_("This request cannot be cancelled."))
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            if rec.state != "cancelled":
                raise UserError(_("Only a cancelled request can be reset."))
            rec.state = "draft"


class OfficeSupplyRequestLine(models.Model):
    _name = "office.supply.request.line"
    _description = "Office Supply Request Line"
    _order = "request_id, sequence, id"

    request_id = fields.Many2one(
        "office.supply.request", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Item / Description", required=True)
    quantity = fields.Float(string="Quantity", required=True, default=1.0)
    note = fields.Char(string="Note")
    company_id = fields.Many2one(
        related="request_id.company_id", store=True, readonly=True)

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_("Quantity must be strictly positive."))
