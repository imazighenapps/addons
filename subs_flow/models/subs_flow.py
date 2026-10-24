# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

INTERVAL_MONTHS = {"monthly": 1, "quarterly": 3, "yearly": 12}


class SubsPlan(models.Model):
    _name = "subs.plan"
    _description = "Subscription Plan"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "product.product", string="Product", required=True,
        domain=[("type", "=", "service")])
    amount = fields.Monetary(currency_field="currency_id", required=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    interval = fields.Selection(
        [("monthly", "Monthly"), ("quarterly", "Quarterly"),
         ("yearly", "Yearly")],
        default="monthly", required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)

    @api.constrains("amount")
    def _check_amount(self):
        for plan in self:
            if plan.amount < 0:
                raise UserError(_("The plan amount cannot be negative."))


class SubsSubscription(models.Model):
    _name = "subs.subscription"
    _description = "Subscription"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True)
    plan_id = fields.Many2one(
        "subs.plan", string="Plan", required=True, tracking=True,
        ondelete="restrict")
    date_start = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    date_next_invoice = fields.Date(tracking=True)
    interval = fields.Selection(
        [("monthly", "Monthly"), ("quarterly", "Quarterly"),
         ("yearly", "Yearly")],
        default="monthly", required=True, tracking=True)
    amount = fields.Monetary(currency_field="currency_id", tracking=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"),
         ("paused", "Paused"), ("closed", "Closed")],
        default="draft", required=True, tracking=True)
    invoice_ids = fields.One2many(
        "account.move", "subscription_id", string="Invoices")
    invoice_count = fields.Integer(compute="_compute_invoice_count")
    mrr = fields.Monetary(
        string="MRR", compute="_compute_mrr", currency_field="currency_id")
    arr = fields.Monetary(
        string="ARR", compute="_compute_mrr", currency_field="currency_id")
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "subs.subscription") or "/"
        return super().create(vals_list)

    @api.onchange("plan_id")
    def _onchange_plan(self):
        if self.plan_id:
            self.amount = self.plan_id.amount
            self.interval = self.plan_id.interval

    @api.depends("amount", "interval")
    def _compute_mrr(self):
        for subscription in self:
            months = INTERVAL_MONTHS.get(subscription.interval, 1)
            subscription.mrr = subscription.amount / months
            subscription.arr = subscription.mrr * 12.0

    @api.depends("invoice_ids")
    def _compute_invoice_count(self):
        for subscription in self:
            subscription.invoice_count = len(subscription.invoice_ids)

    def _next_date(self, current):
        months = INTERVAL_MONTHS.get(self.interval, 1)
        return current + relativedelta(months=months)

    def action_start(self):
        for subscription in self:
            if subscription.state == "running":
                raise UserError(_("This subscription is already running."))
            subscription.write({
                "state": "running",
                "date_next_invoice": subscription.date_next_invoice
                or subscription.date_start,
            })

    def action_pause(self):
        for subscription in self:
            if subscription.state != "running":
                raise UserError(_("Only a running subscription can be paused."))
            subscription.state = "paused"

    def action_resume(self):
        for subscription in self:
            if subscription.state != "paused":
                raise UserError(_("Only a paused subscription can be resumed."))
            subscription.state = "running"

    def action_close(self):
        for subscription in self:
            subscription.state = "closed"

    def _create_invoice(self):
        self.ensure_one()
        journal = self.env["account.journal"].search(
            [("type", "=", "sale"),
             ("company_id", "=", self.company_id.id)], limit=1)
        if not journal:
            raise UserError(_("No sales journal found for this company."))
        product = self.plan_id.product_id
        return self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.partner_id.id,
            "journal_id": journal.id,
            "invoice_date": fields.Date.context_today(self),
            "subscription_id": self.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": product.id,
                "name": _("%(plan)s - %(period)s",
                          plan=self.plan_id.name,
                          period=fields.Date.context_today(self).strftime("%B %Y")),
                "quantity": 1,
                "price_unit": self.amount,
                "tax_ids": [(5, 0, 0)],
            })],
        })

    def action_invoice_now(self):
        for subscription in self:
            if subscription.state == "closed":
                raise UserError(_("A closed subscription cannot be invoiced."))
            invoice = subscription._create_invoice()
            subscription.date_next_invoice = subscription._next_date(
                subscription.date_next_invoice
                or fields.Date.context_today(subscription))
            subscription.message_post(body=_(
                "Invoice %s generated from subscription.", invoice.name))
        return True

    @api.model
    def _cron_invoice(self):
        today = fields.Date.context_today(self)
        subscriptions = self.search([
            ("state", "=", "running"),
            ("date_next_invoice", "<=", today),
        ])
        for subscription in subscriptions:
            try:
                with self.env.cr.savepoint():
                    subscription.action_invoice_now()
            except Exception:
                subscription.message_post(body=_(
                    "Automatic invoicing failed. Please check the plan and the journal."))
        return True

    def action_view_invoices(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Invoices"),
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("subscription_id", "=", self.id)],
            "context": {"default_subscription_id": self.id},
        }


class AccountMove(models.Model):
    _inherit = "account.move"

    subscription_id = fields.Many2one(
        "subs.subscription", string="Subscription", copy=False, index=True)
