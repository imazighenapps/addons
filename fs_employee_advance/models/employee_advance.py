# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class EmployeeAdvance(models.Model):
    _name = "employee.advance"
    _description = "Employee Cash Advance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_request desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True,
        tracking=True)
    department_id = fields.Many2one(
        "hr.department", string="Department",
        related="employee_id.department_id", store=True, readonly=True)
    date_request = fields.Date(
        string="Request Date", required=True,
        default=fields.Date.context_today, tracking=True)
    date_paid = fields.Date(string="Paid Date", readonly=True, copy=False)
    purpose = fields.Char(string="Purpose")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    amount_requested = fields.Monetary(
        string="Requested Amount", currency_field="currency_id",
        required=True, tracking=True)
    amount_approved = fields.Monetary(
        string="Approved Amount", currency_field="currency_id",
        tracking=True)
    amount_cleared = fields.Monetary(
        compute="_compute_amounts", currency_field="currency_id",
        string="Cleared Amount", store=True)
    amount_outstanding = fields.Monetary(
        compute="_compute_amounts", currency_field="currency_id",
        string="Outstanding", store=True)
    clearing_ids = fields.One2many(
        "employee.advance.clearing", "advance_id", string="Clearings",
        copy=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("paid", "Paid"),
         ("partial", "Partially Cleared"), ("cleared", "Cleared"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("amount_approved", "amount_requested", "clearing_ids.amount",
                 "state")
    def _compute_amounts(self):
        for rec in self:
            cleared = sum(rec.clearing_ids.mapped("amount"))
            paid_base = rec.amount_approved or rec.amount_requested or 0.0
            if rec.state in ("draft", "approved", "cancelled"):
                rec.amount_cleared = 0.0
                rec.amount_outstanding = 0.0
            else:
                rec.amount_cleared = cleared
                rec.amount_outstanding = max(paid_base - cleared, 0.0)

    @api.constrains("amount_requested")
    def _check_requested(self):
        for rec in self:
            if rec.amount_requested <= 0:
                raise ValidationError(
                    _("The requested amount must be strictly positive."))

    @api.constrains("amount_approved", "amount_requested")
    def _check_approved(self):
        for rec in self:
            if rec.amount_approved and rec.amount_approved <= 0:
                raise ValidationError(
                    _("The approved amount must be strictly positive."))
            if rec.amount_approved - rec.amount_requested > EPS:
                raise ValidationError(
                    _("The approved amount cannot exceed the requested amount."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("employee.advance")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Employee Advance",
                        "code": "employee.advance",
                        "prefix": "ADV/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def _paid_amount(self):
        self.ensure_one()
        return self.amount_approved or self.amount_requested

    def action_approve(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft advance can be approved."))
            if not rec.amount_approved:
                rec.amount_approved = rec.amount_requested
            rec.state = "approved"

    def action_pay(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError(_("Only an approved advance can be marked paid."))
            rec.write({
                "state": "paid",
                "date_paid": fields.Date.context_today(self),
            })
            rec._recompute_state()

    def action_cancel(self):
        for rec in self:
            if rec.state in ("paid", "partial", "cleared"):
                raise UserError(_("A paid or cleared advance cannot be cancelled."))
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            if rec.state != "cancelled":
                raise UserError(_("Only a cancelled advance can be reset."))
            rec.state = "draft"

    def _recompute_state(self):
        for rec in self:
            if rec.state in ("draft", "approved", "cancelled"):
                continue
            paid = rec._paid_amount()
            cleared = sum(rec.clearing_ids.mapped("amount"))
            if cleared <= EPS:
                rec.state = "paid"
            elif cleared + EPS < paid:
                rec.state = "partial"
            else:
                rec.state = "cleared"


class EmployeeAdvanceClearing(models.Model):
    _name = "employee.advance.clearing"
    _description = "Advance Clearing"
    _order = "advance_id, date, id"

    advance_id = fields.Many2one(
        "employee.advance", required=True, ondelete="cascade", index=True)
    date = fields.Date(
        string="Date", required=True, default=fields.Date.context_today)
    clearing_type = fields.Selection(
        [("expense", "Expense Justification"), ("return", "Cash Return")],
        string="Type", required=True, default="expense")
    amount = fields.Monetary(
        string="Amount", currency_field="currency_id", required=True)
    currency_id = fields.Many2one(
        related="advance_id.currency_id", store=True, readonly=True)
    note = fields.Char(string="Reference / Note")
    company_id = fields.Many2one(
        related="advance_id.company_id", store=True, readonly=True)

    @api.constrains("amount")
    def _check_amount(self):
        for line in self:
            if line.amount <= 0:
                raise ValidationError(
                    _("The clearing amount must be strictly positive."))

    @api.constrains("amount", "advance_id")
    def _check_total(self):
        for line in self:
            adv = line.advance_id
            if adv.state in ("draft", "approved", "cancelled"):
                raise ValidationError(
                    _("Clearings are only allowed on a paid advance."))
            paid = adv._paid_amount()
            total = sum(adv.clearing_ids.mapped("amount"))
            if total - paid > EPS:
                raise ValidationError(
                    _("Clearings (%(total)s) cannot exceed the paid advance "
                      "amount (%(paid)s).", total=total, paid=paid))

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs.mapped("advance_id")._recompute_state()
        return recs

    def write(self, vals):
        res = super().write(vals)
        self.mapped("advance_id")._recompute_state()
        return res

    def unlink(self):
        advances = self.mapped("advance_id")
        res = super().unlink()
        advances._recompute_state()
        return res
