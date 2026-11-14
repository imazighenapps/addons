# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class PurchaseRequisitionRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_request desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    requester_id = fields.Many2one(
        "res.users", string="Requester", default=lambda self: self.env.user,
        required=True, tracking=True, index=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", tracking=True)
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
        "purchase.request.line", "requisition_id", string="Lines", copy=True)
    amount_estimated = fields.Monetary(
        compute="_compute_amount", currency_field="currency_id",
        string="Estimated Total", store=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"),
         ("ordered", "Ordered"), ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text(string="Reason / Notes")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("line_ids.estimated_subtotal")
    def _compute_amount(self):
        for rec in self:
            rec.amount_estimated = sum(rec.line_ids.mapped("estimated_subtotal"))

    @api.constrains("line_ids")
    def _check_lines(self):
        for rec in self:
            if rec.state != "draft" and not rec.line_ids:
                raise ValidationError(_("A requisition must contain at least one line."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("purchase.request")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Purchase Request",
                        "code": "purchase.request",
                        "prefix": "PRQ/%(year)s/",
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
                raise UserError(_("Only a draft requisition can be submitted."))
            rec._ensure_lines()
            rec.state = "submitted"

    def action_approve(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only a submitted requisition can be approved."))
            rec._ensure_lines()
            rec.state = "approved"

    def action_ordered(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError(_("Only an approved requisition can be marked ordered."))
            rec.state = "ordered"

    def action_done(self):
        for rec in self:
            if rec.state != "ordered":
                raise UserError(_("Only an ordered requisition can be marked done."))
            rec.state = "done"

    def action_cancel(self):
        for rec in self:
            if rec.state in ("done", "cancelled"):
                raise UserError(_("This requisition cannot be cancelled."))
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            if rec.state != "cancelled":
                raise UserError(_("Only a cancelled requisition can be reset."))
            rec.state = "draft"


class PurchaseRequisitionLine(models.Model):
    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _order = "requisition_id, sequence, id"

    requisition_id = fields.Many2one(
        "purchase.request", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one("product.product", string="Product")
    name = fields.Char(string="Description", required=True)
    quantity = fields.Float(string="Quantity", required=True, default=1.0)
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    price_unit = fields.Monetary(
        string="Estimated Unit Price", currency_field="currency_id")
    estimated_subtotal = fields.Monetary(
        compute="_compute_subtotal", currency_field="currency_id",
        string="Estimated Subtotal", store=True)
    currency_id = fields.Many2one(
        related="requisition_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="requisition_id.company_id", store=True, readonly=True)

    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for line in self:
            line.estimated_subtotal = (line.quantity or 0.0) * (line.price_unit or 0.0)

    @api.onchange("product_id")
    def _onchange_product(self):
        for line in self:
            if line.product_id:
                line.name = line.product_id.display_name
                if "uom_id" in line.product_id._fields:
                    line.uom_id = line.product_id.uom_id
                if "standard_price" in line.product_id._fields and not line.price_unit:
                    line.price_unit = line.product_id.standard_price

    @api.constrains("quantity", "price_unit")
    def _check_values(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_("Quantity must be strictly positive."))
            if (line.price_unit or 0.0) < -EPS:
                raise ValidationError(_("Estimated unit price cannot be negative."))
