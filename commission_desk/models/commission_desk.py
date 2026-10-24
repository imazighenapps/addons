# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CommissionRule(models.Model):
    _name = "commission.rule"
    _description = "Commission Rule"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    user_id = fields.Many2one("res.users", string="Salesperson")
    team_id = fields.Many2one("crm.team", string="Sales Team")
    partner_id = fields.Many2one("res.partner", string="Customer")
    product_category_id = fields.Many2one("product.category", string="Product Category")
    basis = fields.Selection(
        [("order", "Confirmed Order"),
         ("invoice", "Posted Invoice"),
         ("payment", "Registered Payment")],
        default="order", required=True,
        help="Moment when the commission is earned.")
    rate_type = fields.Selection(
        [("percent", "Percentage"),
         ("fixed", "Fixed Amount")],
        default="percent", required=True)
    rate = fields.Float(
        string="Rate / Amount", digits=(16, 4),
        help="Percentage of the base, or fixed amount per document.")
    use_margin = fields.Boolean(
        string="Calculate on Margin",
        help="Use the margin (sale price minus product cost) instead of the revenue.")
    date_start = fields.Date()
    date_end = fields.Date()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    tier_ids = fields.One2many("commission.tier", "rule_id", string="Volume Tiers")
    note = fields.Text()

    @api.constrains("rate")
    def _check_rate(self):
        for rule in self:
            if rule.rate < 0:
                raise ValidationError(_("The commission rate cannot be negative."))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rule in self:
            if rule.date_start and rule.date_end and rule.date_start > rule.date_end:
                raise ValidationError(_("The start date must be before the end date."))


class CommissionTier(models.Model):
    _name = "commission.tier"
    _description = "Commission Volume Tier"
    _order = "min_amount, id"

    rule_id = fields.Many2one("commission.rule", required=True, ondelete="cascade")
    min_amount = fields.Monetary(currency_field="currency_id", required=True)
    max_amount = fields.Monetary(
        currency_field="currency_id",
        help="Leave empty for no upper limit.")
    rate = fields.Float(string="Rate (%)", digits=(16, 4), required=True)
    currency_id = fields.Many2one(
        related="rule_id.company_id.currency_id", store=True, readonly=True)

    @api.constrains("min_amount", "max_amount")
    def _check_range(self):
        for tier in self:
            if tier.max_amount and tier.min_amount > tier.max_amount:
                raise ValidationError(_("The minimum amount cannot exceed the maximum amount."))


class CommissionLine(models.Model):
    _name = "commission.line"
    _description = "Commission Line"
    _order = "date desc, id desc"

    name = fields.Char(default="/", required=True)
    statement_id = fields.Many2one(
        "commission.statement", ondelete="cascade", index=True)
    rule_id = fields.Many2one("commission.rule", ondelete="restrict")
    user_id = fields.Many2one("res.users", string="Salesperson", required=True)
    partner_id = fields.Many2one("res.partner", string="Customer")
    sale_order_id = fields.Many2one("sale.order", string="Sales Order")
    invoice_id = fields.Many2one("account.move", string="Invoice / Credit Note")
    payment_id = fields.Many2one("account.payment", string="Payment")
    date = fields.Date(default=fields.Date.context_today, required=True)
    base_amount = fields.Monetary(currency_field="currency_id")
    rate = fields.Float(digits=(16, 4))
    amount = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"),
         ("paid", "Paid"), ("cancelled", "Cancelled")],
        default="draft", required=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    note = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("commission.line") or "/"
        return super().create(vals_list)


class CommissionStatement(models.Model):
    _name = "commission.statement"
    _description = "Commission Statement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Salesperson", required=True, tracking=True)
    date_from = fields.Date(required=True, tracking=True)
    date_to = fields.Date(required=True, tracking=True)
    line_ids = fields.One2many("commission.line", "statement_id", string="Lines")
    total_base = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True)
    total_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("paid", "Paid"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    approved_by = fields.Many2one("res.users", readonly=True)
    approved_date = fields.Datetime(readonly=True)
    payment_date = fields.Date(readonly=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("commission.statement") or "/"
        return super().create(vals_list)

    @api.depends("line_ids.base_amount", "line_ids.amount", "line_ids.state")
    def _compute_totals(self):
        for statement in self:
            lines = statement.line_ids.filtered(lambda l: l.state != "cancelled")
            statement.total_base = sum(lines.mapped("base_amount"))
            statement.total_amount = sum(lines.mapped("amount"))

    def _find_rule(self, user, team, partner, category, date):
        """Return the most specific active rule for this context."""
        rules = self.env["commission.rule"].search([
            ("active", "=", True),
            ("company_id", "in", [self.company_id.id, False]),
        ])
        best = self.env["commission.rule"]
        best_score = -1
        for rule in rules:
            if rule.date_start and rule.date_start > date:
                continue
            if rule.date_end and rule.date_end < date:
                continue
            if rule.user_id and rule.user_id != user:
                continue
            if rule.team_id and rule.team_id != team:
                continue
            if rule.partner_id and rule.partner_id != partner:
                continue
            if rule.product_category_id and rule.product_category_id != category:
                continue
            score = 0
            if rule.user_id:
                score += 8
            if rule.team_id:
                score += 4
            if rule.partner_id:
                score += 2
            if rule.product_category_id:
                score += 1
            if score > best_score:
                best = rule
                best_score = score
        return best

    def _rate_for(self, rule, base):
        tier = rule.tier_ids.filtered(
            lambda t: base >= t.min_amount
            and (not t.max_amount or base <= t.max_amount))[:1]
        if tier:
            return tier.rate
        return rule.rate

    def _amount_for(self, rule, base):
        rate = self._rate_for(rule, base)
        if rule.rate_type == "fixed":
            return rate, rate
        return rate, base * rate / 100.0

    def _prepare_line(self, rule, user, partner, date, base,
                      order=None, invoice=None, payment=None, note=None):
        rate, amount = self._amount_for(rule, base)
        return {
            "statement_id": self.id,
            "rule_id": rule.id,
            "user_id": user.id,
            "partner_id": partner.id if partner else False,
            "sale_order_id": order.id if order else False,
            "invoice_id": invoice.id if invoice else False,
            "payment_id": payment.id if payment else False,
            "date": date,
            "base_amount": base,
            "rate": rate,
            "amount": amount,
            "state": "draft",
            "currency_id": self.currency_id.id,
            "company_id": self.company_id.id,
            "note": note,
        }

    def _generate_orders(self):
        orders = self.env["sale.order"].search([
            ("state", "=", "sale"),
            ("date_order", ">=", self.date_from),
            ("date_order", "<=", self.date_to),
            ("company_id", "=", self.company_id.id),
            ("user_id", "=", self.user_id.id),
        ])
        existing = self.env["commission.line"].search([
            ("sale_order_id", "in", orders.ids),
            ("user_id", "=", self.user_id.id),
            ("state", "!=", "cancelled"),
        ]).mapped("sale_order_id")
        vals_list = []
        for order in orders - existing:
            for line in order.order_line.filtered(lambda l: not l.display_type):
                category = line.product_id.categ_id
                rule = self._find_rule(
                    order.user_id, order.team_id, order.partner_id,
                    category, order.date_order.date())
                if not rule or rule.basis != "order":
                    continue
                if rule.use_margin:
                    base = line.price_subtotal - (line.product_id.standard_price * line.product_uom_qty)
                else:
                    base = line.price_subtotal
                vals_list.append(self._prepare_line(
                    rule, order.user_id, order.partner_id,
                    order.date_order.date(), base,
                    order=order, note=line.product_id.display_name))
        if vals_list:
            self.env["commission.line"].create(vals_list)

    def _generate_invoices(self):
        invoices = self.env["account.move"].search([
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("invoice_date", ">=", self.date_from),
            ("invoice_date", "<=", self.date_to),
            ("company_id", "=", self.company_id.id),
            ("invoice_user_id", "=", self.user_id.id),
        ])
        existing = self.env["commission.line"].search([
            ("invoice_id", "in", invoices.ids),
            ("user_id", "=", self.user_id.id),
            ("state", "!=", "cancelled"),
        ]).mapped("invoice_id")
        vals_list = []
        for invoice in invoices - existing:
            for line in invoice.invoice_line_ids.filtered(lambda l: not l.display_type):
                category = line.product_id.categ_id
                rule = self._find_rule(
                    invoice.invoice_user_id, False, invoice.partner_id,
                    category, invoice.invoice_date)
                if not rule or rule.basis != "invoice":
                    continue
                if rule.use_margin:
                    base = line.price_subtotal - (line.product_id.standard_price * line.quantity)
                else:
                    base = line.price_subtotal
                vals_list.append(self._prepare_line(
                    rule, invoice.invoice_user_id, invoice.partner_id,
                    invoice.invoice_date, base,
                    invoice=invoice, note=line.product_id.display_name))
        if vals_list:
            self.env["commission.line"].create(vals_list)

    def _generate_payments(self):
        payments = self.env["account.payment"].search([
            ("state", "in", ["paid", "in_process"]),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("partner_type", "=", "customer"),
            ("company_id", "=", self.company_id.id),
        ])
        existing = self.env["commission.line"].search([
            ("payment_id", "in", payments.ids),
            ("user_id", "=", self.user_id.id),
            ("state", "!=", "cancelled"),
        ]).mapped("payment_id")
        vals_list = []
        for payment in payments - existing:
            rule = self._find_rule(
                self.user_id, False, payment.partner_id, False, payment.date)
            if not rule or rule.basis != "payment":
                continue
            vals_list.append(self._prepare_line(
                rule, self.user_id, payment.partner_id,
                payment.date, payment.amount, payment=payment))
        if vals_list:
            self.env["commission.line"].create(vals_list)

    def action_generate_lines(self):
        for statement in self:
            if statement.state != "draft":
                raise UserError(_("You can only generate lines on a draft statement."))
            statement.line_ids.filtered(lambda l: l.state == "draft").unlink()
            statement._generate_orders()
            statement._generate_invoices()
            statement._generate_payments()
            if not statement.line_ids:
                raise UserError(_(
                    "No commission line was found for this period. "
                    "Check the rules, the salesperson and the dates."))
        return True

    def action_clawback(self):
        """Create negative lines for customer credit notes in the period."""
        for statement in self:
            refunds = self.env["account.move"].search([
                ("move_type", "=", "out_refund"),
                ("state", "=", "posted"),
                ("invoice_date", ">=", statement.date_from),
                ("invoice_date", "<=", statement.date_to),
                ("company_id", "=", statement.company_id.id),
                ("invoice_user_id", "=", statement.user_id.id),
            ])
            existing = statement.line_ids.mapped("invoice_id")
            vals_list = []
            for refund in refunds - existing:
                for line in refund.invoice_line_ids.filtered(lambda l: not l.display_type):
                    rule = statement._find_rule(
                        refund.invoice_user_id, False, refund.partner_id,
                        line.product_id.categ_id, refund.invoice_date)
                    if not rule or rule.basis != "invoice":
                        continue
                    base = -line.price_subtotal
                    vals_list.append(statement._prepare_line(
                        rule, refund.invoice_user_id, refund.partner_id,
                        refund.invoice_date, base,
                        invoice=refund, note=_("Clawback: %s") % refund.name))
            if vals_list:
                self.env["commission.line"].create(vals_list)
        return True

    def action_submit(self):
        for statement in self:
            if not statement.line_ids:
                raise UserError(_("Add at least one commission line before submitting."))
            statement.state = "submitted"

    def action_approve(self):
        for statement in self:
            if statement.state != "submitted":
                raise UserError(_("Only a submitted statement can be approved."))
            statement.write({
                "state": "approved",
                "approved_by": self.env.user.id,
                "approved_date": fields.Datetime.now(),
            })

    def action_pay(self):
        for statement in self:
            if statement.state != "approved":
                raise UserError(_("Only an approved statement can be marked as paid."))
            statement.write({
                "state": "paid",
                "payment_date": fields.Date.context_today(statement),
            })
            statement.line_ids.write({"state": "paid"})

    def action_cancel(self):
        for statement in self:
            statement.state = "cancelled"
            statement.line_ids.write({"state": "cancelled"})

    def action_reset(self):
        for statement in self:
            if statement.state == "paid":
                raise UserError(_("A paid statement cannot be reset."))
            statement.state = "draft"
            statement.line_ids.write({"state": "draft"})


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commission_line_ids = fields.One2many(
        "commission.line", "sale_order_id", string="Commission Lines")
    commission_total = fields.Monetary(
        string="Commission", compute="_compute_commission_total",
        currency_field="currency_id")

    @api.depends("commission_line_ids.amount", "commission_line_ids.state")
    def _compute_commission_total(self):
        for order in self:
            order.commission_total = sum(
                order.commission_line_ids.filtered(
                    lambda l: l.state != "cancelled").mapped("amount"))

    def action_view_commissions(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "commission_desk.action_commission_line")
        action["domain"] = [("sale_order_id", "=", self.id)]
        action["context"] = {"default_sale_order_id": self.id}
        return action
