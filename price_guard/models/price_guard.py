# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PriceAgreement(models.Model):
    _name = "price.agreement"
    _description = "Supplier Price Agreement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "partner_id, product_id, date_from desc"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", required=True,
        domain=[("supplier_rank", ">", 0)], tracking=True, index=True)
    product_id = fields.Many2one(
        "product.product", string="Product", required=True,
        tracking=True, index=True)
    price = fields.Monetary(
        string="Agreed Price", currency_field="currency_id",
        required=True, tracking=True,
        help="Unit price negotiated with the supplier, in the company "
             "currency.")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    min_qty = fields.Float(
        string="Minimum Quantity", default=1.0,
        help="The agreement applies from this quantity.")
    date_from = fields.Date(
        required=True, tracking=True, default=fields.Date.context_today)
    date_to = fields.Date(tracking=True)
    tolerance_percent = fields.Float(
        string="Tolerance (%)", default=2.0, tracking=True,
        help="A price above the agreed price by up to this percentage is "
             "accepted. Up to twice this value a warning is raised, above "
             "that the check is a breach.")
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"),
         ("expired", "Expired")],
        default="draft", required=True, tracking=True, index=True)
    check_ids = fields.One2many(
        "price.check", "agreement_id", string="Price Checks")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    @api.constrains("price")
    def _check_price(self):
        for agreement in self:
            if agreement.price <= 0:
                raise ValidationError(_(
                    "The agreed price must be greater than zero."))

    @api.constrains("tolerance_percent")
    def _check_tolerance(self):
        for agreement in self:
            if agreement.tolerance_percent < 0:
                raise ValidationError(_(
                    "The tolerance cannot be negative."))

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for agreement in self:
            if agreement.date_from and agreement.date_to \
                    and agreement.date_to < agreement.date_from:
                raise ValidationError(_(
                    "The end date must be on or after the start date."))

    def action_activate(self):
        for agreement in self:
            if agreement.state != "draft":
                raise UserError(_(
                    "Only a draft agreement can be activated."))
            agreement.write({"state": "running"})
        return True

    def action_expire(self):
        for agreement in self:
            agreement.write({"state": "expired"})
        return True

    def action_reset(self):
        for agreement in self:
            agreement.write({"state": "draft"})
        return True


class PriceCheck(models.Model):
    _name = "price.check"
    _description = "Supplier Price Check"
    _order = "date desc, id desc"

    name = fields.Char(default="/", required=True)
    agreement_id = fields.Many2one(
        "price.agreement", string="Agreement", ondelete="set null",
        index=True)
    invoice_line_id = fields.Many2one(
        "account.move.line", string="Invoice Line", ondelete="cascade",
        index=True)
    invoice_id = fields.Many2one(
        "account.move", string="Vendor Bill", ondelete="cascade",
        index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", index=True)
    product_id = fields.Many2one(
        "product.product", string="Product", index=True)
    date = fields.Date()
    quantity = fields.Float()
    invoice_price = fields.Monetary(
        string="Invoiced Price", currency_field="currency_id")
    agreed_price = fields.Monetary(
        string="Agreed Price", currency_field="currency_id")
    difference_percent = fields.Float(
        string="Difference (%)", compute="_compute_difference", store=True)
    status = fields.Selection(
        [("ok", "Compliant"), ("warning", "Warning"),
         ("breach", "Breach"), ("ignored", "Ignored")],
        default="ok", required=True, index=True)
    state = fields.Selection(
        related="status", string="Status", readonly=True, store=True,
        help="Read-only alias of the status, used by the status bar.")
    note = fields.Text()
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)

    _invoice_line_agreement_uniq = models.Constraint(
        "unique(invoice_line_id, agreement_id)",
        "A price check already exists for this invoice line and agreement.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "price.check") or "/"
        return super().create(vals_list)

    @api.depends("invoice_price", "agreed_price")
    def _compute_difference(self):
        for check in self:
            if check.agreed_price:
                check.difference_percent = (
                    (check.invoice_price - check.agreed_price)
                    / check.agreed_price * 100.0)
            else:
                check.difference_percent = 0.0

    @api.model
    def _status_for(self, difference, tolerance):
        tolerance = tolerance or 0.0
        if difference <= tolerance:
            return "ok"
        if difference <= 2.0 * tolerance:
            return "warning"
        return "breach"

    def action_ignore(self):
        self.write({"status": "ignored"})
        return True

    def action_reset(self):
        for check in self:
            tolerance = check.agreement_id.tolerance_percent \
                if check.agreement_id else 0.0
            check.status = self._status_for(
                check.difference_percent, tolerance)
        return True


class PriceScanner(models.Model):
    _name = "price.scanner"
    _description = "Supplier Price Scanner"

    @api.model
    def _find_agreement(self, line, invoice, allowed=None):
        move_date = invoice.invoice_date or invoice.date \
            or fields.Date.context_today(invoice)
        domain = [
            ("state", "=", "running"),
            ("partner_id", "=", invoice.partner_id.id),
            ("product_id", "=", line.product_id.id),
            ("company_id", "=", invoice.company_id.id),
            ("date_from", "<=", move_date),
            "|", ("date_to", "=", False), ("date_to", ">=", move_date),
        ]
        if allowed is not None:
            domain.append(("id", "in", allowed.ids))
        agreements = self.env["price.agreement"].search(
            domain, order="min_qty desc, date_from desc, id desc")
        for agreement in agreements:
            if line.quantity >= agreement.min_qty:
                return agreement
        return self.env["price.agreement"]

    @api.model
    def action_scan(self, agreement_ids=None):
        allowed = None
        if agreement_ids:
            if isinstance(agreement_ids, models.BaseModel):
                allowed = agreement_ids
            else:
                allowed = self.env["price.agreement"].browse(agreement_ids)
        domain = [("state", "=", "running")]
        if allowed is not None:
            domain.append(("id", "in", allowed.ids))
        agreements = self.env["price.agreement"].search(domain)
        if not agreements:
            return 0
        partners = agreements.mapped("partner_id")
        invoices = self.env["account.move"].search([
            ("move_type", "in", ["in_invoice", "in_refund"]),
            ("state", "=", "posted"),
            ("partner_id", "in", partners.ids),
        ], order="invoice_date, id")
        created = 0
        for invoice in invoices:
            for line in invoice.invoice_line_ids:
                if not line.product_id \
                        or line.display_type not in (False, "product"):
                    continue
                agreement = self._find_agreement(line, invoice, agreements)
                if not agreement:
                    continue
                exists = self.env["price.check"].search_count([
                    ("invoice_line_id", "=", line.id),
                    ("agreement_id", "=", agreement.id),
                ])
                if exists:
                    continue
                move_date = invoice.invoice_date or invoice.date \
                    or fields.Date.context_today(invoice)
                currency = agreement.currency_id \
                    or invoice.company_id.currency_id
                invoice_price = invoice.currency_id._convert(
                    abs(line.price_unit), currency,
                    invoice.company_id, move_date)
                difference = (
                    (invoice_price - agreement.price)
                    / agreement.price * 100.0) if agreement.price else 0.0
                self.env["price.check"].create({
                    "agreement_id": agreement.id,
                    "invoice_line_id": line.id,
                    "invoice_id": invoice.id,
                    "partner_id": invoice.partner_id.id,
                    "product_id": line.product_id.id,
                    "date": move_date,
                    "quantity": line.quantity,
                    "invoice_price": invoice_price,
                    "agreed_price": agreement.price,
                    "currency_id": currency.id,
                    "status": self.env["price.check"]._status_for(
                        difference, agreement.tolerance_percent),
                })
                created += 1
        return created

    @api.model
    def action_scan_ui(self):
        created = self.action_scan()
        return {
            "type": "ir.actions.act_window",
            "name": _("Price Checks"),
            "res_model": "price.check",
            "view_mode": "list,form",
            "domain": [("status", "in", ["warning", "breach"])],
            "help": _("%s new price check(s) created.", created),
        }
