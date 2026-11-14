# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

EPS = 1e-6


class SalePlanPay(models.Model):
    _name = "sale.plan.pay"
    _description = "Sale Payment Plan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    order_id = fields.Many2one(
        "sale.order", string="Sale Order", required=True, index=True,
        tracking=True, domain="[('state', 'in', ('sale', 'done'))]",
        help="The confirmed sale order this installment plan belongs to.")
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True,
        tracking=True)
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    amount_total = fields.Monetary(
        string="Order Amount", currency_field="currency_id", required=True,
        tracking=True)
    line_ids = fields.One2many(
        "sale.plan.pay.line", "plan_id", string="Installments", copy=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"),
         ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    amount_planned = fields.Monetary(
        compute="_compute_amounts", currency_field="currency_id",
        string="Planned Amount", store=True)
    amount_invoiced = fields.Monetary(
        compute="_compute_amounts", currency_field="currency_id",
        string="Invoiced Amount", store=True)
    amount_paid = fields.Monetary(
        compute="_compute_amounts", currency_field="currency_id",
        string="Paid Amount", store=True)
    late_count = fields.Integer(
        compute="_compute_amounts", string="Late Installments", store=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("line_ids.amount", "line_ids.status", "line_ids.move_id",
                 "line_ids.move_id.payment_state",
                 "line_ids.move_id.amount_residual")
    def _compute_amounts(self):
        for rec in self:
            rec.amount_planned = sum(rec.line_ids.mapped("amount"))
            rec.amount_invoiced = sum(
                rec.line_ids.filtered(
                    lambda l: l.status in ("invoiced", "paid", "late")
                ).mapped("amount"))
            rec.amount_paid = sum(
                rec.line_ids.filtered(
                    lambda l: l.status == "paid").mapped("amount"))
            rec.late_count = len(rec.line_ids.filtered(
                lambda l: l.status == "late"))

    @api.onchange("order_id")
    def _onchange_order(self):
        if self.order_id:
            self.partner_id = self.order_id.partner_id
            self.currency_id = self.order_id.currency_id
            self.company_id = self.order_id.company_id
            self.amount_total = self.order_id.amount_total

    @api.constrains("amount_total")
    def _check_amount_total(self):
        for rec in self:
            if rec.amount_total <= 0:
                raise ValidationError(_(
                    "The order amount must be strictly positive."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("sale.plan.pay")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Sale Payment Plan",
                        "code": "sale.plan.pay",
                        "prefix": "SPP/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_activate(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Add at least one installment."))
            total = sum(rec.line_ids.mapped("amount"))
            if abs(total - rec.amount_total) > EPS:
                raise UserError(_(
                    "The sum of installments (%(sum)s) must equal the order "
                    "amount (%(total)s).",
                    sum=total, total=rec.amount_total))
            rec.state = "active"

    def action_done(self):
        for rec in self:
            rec.state = "done"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"


class SalePlanPayLine(models.Model):
    _name = "sale.plan.pay.line"
    _description = "Installment"
    _order = "plan_id, date_due, id"

    plan_id = fields.Many2one(
        "sale.plan.pay", required=True, ondelete="cascade", index=True)
    name = fields.Char(string="Label", required=True)
    date_due = fields.Date(string="Due Date", required=True, index=True)
    amount = fields.Monetary(
        string="Amount", currency_field="currency_id", required=True)
    currency_id = fields.Many2one(
        related="plan_id.currency_id", store=True, readonly=True)
    partner_id = fields.Many2one(
        related="plan_id.partner_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="plan_id.company_id", store=True, readonly=True)
    move_id = fields.Many2one(
        "account.move", string="Invoice", readonly=True, copy=False)
    status = fields.Selection(
        [("planned", "Planned"), ("invoiced", "Invoiced"),
         ("paid", "Paid"), ("late", "Late")],
        compute="_compute_status", string="Status", store=True)

    @api.depends("move_id", "move_id.payment_state", "move_id.state",
                 "move_id.amount_residual", "date_due")
    def _compute_status(self):
        today = fields.Date.context_today(self)
        for line in self:
            move = line.move_id
            if move and move.state == "posted":
                paid_states = {"paid", "in_payment", "reversed"}
                residual = getattr(move, "amount_residual", 0.0) or 0.0
                pstate = getattr(move, "payment_state", None)
                if pstate in paid_states or abs(residual) <= EPS:
                    line.status = "paid"
                    continue
                if line.date_due and line.date_due < today:
                    line.status = "late"
                    continue
                line.status = "invoiced"
                continue
            if move:
                if line.date_due and line.date_due < today:
                    line.status = "late"
                else:
                    line.status = "invoiced"
                continue
            if line.date_due and line.date_due < today:
                line.status = "late"
            else:
                line.status = "planned"

    @api.constrains("amount")
    def _check_amount(self):
        for line in self:
            if line.amount <= 0:
                raise ValidationError(_(
                    "The installment amount must be strictly positive."))

    def action_create_invoice(self):
        self.ensure_one()
        if self.move_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "account.move",
                "res_id": self.move_id.id,
                "view_mode": "form",
            }
        plan = self.plan_id
        if plan.state not in ("active", "done"):
            raise UserError(_(
                "Activate the payment plan before generating an invoice."))
        journal = self.env["account.journal"].search([
            ("type", "=", "sale"), ("company_id", "=", plan.company_id.id),
        ], limit=1)
        move_vals = {
            "move_type": "out_invoice",
            "partner_id": plan.partner_id.id,
            "invoice_origin": "%s / %s" % (plan.order_id.name, self.name),
            "company_id": plan.company_id.id,
            "currency_id": plan.currency_id.id,
            "invoice_date": self.date_due,
            "invoice_line_ids": [(0, 0, {
                "name": "%s - %s" % (plan.order_id.name, self.name),
                "quantity": 1.0,
                "price_unit": self.amount,
            })],
        }
        if journal:
            move_vals["journal_id"] = journal.id
        move = self.env["account.move"].create(move_vals)
        self.move_id = move.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
        }
