# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CreditProfile(models.Model):
    _name = "credit.profile"
    _description = "Customer Credit Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "partner_id"

    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True,
        ondelete="cascade", tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    credit_limit = fields.Monetary(
        currency_field="currency_id", tracking=True,
        help="Maximum exposure allowed for this customer. Zero means no limit.")
    block_mode = fields.Selection(
        [("warn", "Warn the salesperson"),
         ("block", "Block order confirmation")],
        default="block", required=True, tracking=True)
    state = fields.Selection(
        [("active", "Active"), ("blocked", "Blocked")],
        default="active", required=True, tracking=True)
    exposure = fields.Monetary(
        string="Current Exposure", currency_field="currency_id",
        compute="_compute_exposure",
        help="Open invoices plus confirmed orders not yet invoiced.")
    available = fields.Monetary(
        string="Available Credit", currency_field="currency_id",
        compute="_compute_exposure", search="_search_available")
    usage = fields.Float(
        string="Usage (%)", compute="_compute_exposure")
    overdue_amount = fields.Monetary(
        string="Overdue", currency_field="currency_id",
        compute="_compute_exposure", search="_search_overdue_amount")
    overdue_days = fields.Integer(
        string="Overdue Days", compute="_compute_exposure")
    invoice_count = fields.Integer(compute="_compute_exposure")
    order_count = fields.Integer(compute="_compute_exposure")
    note = fields.Text()
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('partner_company_uniq', "unique(partner_id, company_id)", "A credit profile already exists for this customer."),
    ]

    @api.depends("partner_id", "company_id")
    def _compute_exposure(self):
        Move = self.env["account.move"]
        Order = self.env["sale.order"]
        today = fields.Date.context_today(self)
        for profile in self:
            if not profile.partner_id:
                profile.exposure = 0.0
                profile.available = 0.0
                profile.usage = 0.0
                profile.overdue_amount = 0.0
                profile.overdue_days = 0
                profile.invoice_count = 0
                profile.order_count = 0
                continue
            domain = [
                ("partner_id", "=", profile.partner_id.id),
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "=", "posted"),
                ("payment_state", "not in", ["paid", "reversed"]),
                ("company_id", "=", profile.company_id.id),
            ]
            invoices = Move.search(domain)
            orders = Order.search([
                ("partner_id", "=", profile.partner_id.id),
                ("state", "=", "sale"),
                ("invoice_status", "=", "to invoice"),
                ("company_id", "=", profile.company_id.id),
            ])
            exposure = sum(invoices.mapped("amount_residual_signed")) \
                + sum(orders.mapped("amount_total"))
            overdue = invoices.filtered(
                lambda m: m.invoice_date_due and m.invoice_date_due < today)
            days = 0
            for move in overdue:
                days = max(days, (today - move.invoice_date_due).days)
            profile.exposure = exposure
            profile.available = (profile.credit_limit or 0.0) - exposure
            profile.usage = (
                exposure / profile.credit_limit * 100.0
                if profile.credit_limit else 0.0)
            profile.overdue_amount = sum(overdue.mapped("amount_residual_signed"))
            profile.overdue_days = days
            profile.invoice_count = len(invoices)
            profile.order_count = len(orders)

    @api.constrains("credit_limit")
    def _check_limit(self):
        for profile in self:
            if profile.credit_limit < 0:
                raise ValidationError(_("The credit limit cannot be negative."))

    @staticmethod
    def _match(value, operator, reference):
        if operator in ("=", "=="):
            return value == reference
        if operator == "!=":
            return value != reference
        if operator == ">":
            return value > reference
        if operator == ">=":
            return value >= reference
        if operator == "<":
            return value < reference
        if operator == "<=":
            return value <= reference
        return True

    def _search_available(self, operator, value):
        ids = [p.id for p in self.search([])
               if self._match(p.available, operator, value)]
        return [("id", "in", ids)]

    def _search_overdue_amount(self, operator, value):
        ids = [p.id for p in self.search([])
               if self._match(p.overdue_amount, operator, value)]
        return [("id", "in", ids)]

    def action_block(self):
        self.write({"state": "blocked"})

    def action_unblock(self):
        self.write({"state": "active"})

    def action_open_invoices(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Open Invoices"),
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [
                ("partner_id", "=", self.partner_id.id),
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "=", "posted"),
                ("payment_state", "not in", ["paid", "reversed"]),
            ],
        }


class CreditOverride(models.Model):
    _name = "credit.override"
    _description = "Credit Limit Override"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True)
    sale_order_id = fields.Many2one("sale.order", string="Sales Order")
    amount = fields.Monetary(currency_field="currency_id", tracking=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    date = fields.Date(default=fields.Date.context_today, required=True)
    reason = fields.Text(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("refused", "Refused")],
        default="draft", required=True, tracking=True)
    requested_by = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True)
    approved_by = fields.Many2one("res.users", readonly=True)
    approved_date = fields.Datetime(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "credit.override") or "/"
        return super().create(vals_list)

    def action_approve(self):
        for override in self:
            if override.state != "draft":
                raise UserError(_("Only a draft request can be approved."))
            override.write({
                "state": "approved",
                "approved_by": self.env.user.id,
                "approved_date": fields.Datetime.now(),
            })

    def action_refuse(self):
        for override in self:
            if override.state != "draft":
                raise UserError(_("Only a draft request can be refused."))
            override.write({"state": "refused"})

    def action_reset(self):
        self.write({
            "state": "draft", "approved_by": False, "approved_date": False})


class SaleOrder(models.Model):
    _inherit = "sale.order"

    credit_profile_id = fields.Many2one(
        "credit.profile", string="Credit Profile",
        compute="_compute_credit_profile")
    credit_exposure = fields.Monetary(
        string="Credit Exposure", currency_field="currency_id",
        compute="_compute_credit_profile")
    credit_available = fields.Monetary(
        string="Available Credit", currency_field="currency_id",
        compute="_compute_credit_profile")
    credit_state = fields.Selection(
        [("ok", "Within Limit"), ("warn", "Over Limit"),
         ("blocked", "Blocked"), ("none", "No Profile")],
        compute="_compute_credit_profile", string="Credit Status")
    credit_override_id = fields.Many2one(
        "credit.override", string="Credit Override", copy=False)

    def _get_credit_profile(self):
        self.ensure_one()
        return self.env["credit.profile"].search([
            ("partner_id", "=", self.partner_id.id),
            ("company_id", "=", self.company_id.id),
        ], limit=1)

    @api.depends("partner_id", "amount_total", "company_id")
    def _compute_credit_profile(self):
        for order in self:
            profile = order._get_credit_profile() if order.partner_id else False
            if not profile:
                order.credit_profile_id = False
                order.credit_exposure = 0.0
                order.credit_available = 0.0
                order.credit_state = "none"
                continue
            profile.invalidate_recordset(["exposure", "available"])
            projected = profile.exposure + order.amount_total
            order.credit_profile_id = profile.id
            order.credit_exposure = projected
            order.credit_available = (profile.credit_limit or 0.0) - projected
            if profile.state == "blocked":
                order.credit_state = "blocked"
            elif profile.credit_limit and projected > profile.credit_limit:
                order.credit_state = "blocked" if profile.block_mode == "block" else "warn"
            else:
                order.credit_state = "ok"

    def action_confirm(self):
        for order in self:
            profile = order._get_credit_profile()
            if not profile or profile.state != "active" or not profile.credit_limit:
                continue
            profile.invalidate_recordset(["exposure"])
            projected = profile.exposure + order.amount_total
            if projected <= profile.credit_limit:
                continue
            override = order.credit_override_id
            if override and override.state == "approved":
                order.message_post(body=_(
                    "Credit limit exceeded but approved by override %s.",
                    override.name))
                continue
            message = _(
                "Customer %(partner)s is over its credit limit: "
                "limit %(limit).2f, projected exposure %(projected).2f.",
                partner=order.partner_id.display_name,
                limit=profile.credit_limit, projected=projected)
            if profile.block_mode == "block":
                raise UserError(message)
            order.message_post(body=message)
        return super().action_confirm()

    def action_request_override(self):
        self.ensure_one()
        profile = self._get_credit_profile()
        override = self.env["credit.override"].create({
            "partner_id": self.partner_id.id,
            "sale_order_id": self.id,
            "amount": self.amount_total,
            "reason": _("Requested from quotation %s") % self.name,
        })
        self.credit_override_id = override.id
        return {
            "type": "ir.actions.act_window",
            "name": _("Credit Override"),
            "res_model": "credit.override",
            "res_id": override.id,
            "view_mode": "form",
            "target": "current",
        }
