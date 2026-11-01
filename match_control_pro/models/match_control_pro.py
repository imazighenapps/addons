# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MatchCheck(models.Model):
    _name = "match.check"
    _description = "Three-Way Match Check"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        default="/", required=True, copy=False, tracking=True, index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Vendor", required=True, tracking=True,
        domain=[("supplier_rank", ">", 0)])
    purchase_id = fields.Many2one(
        "purchase.order", string="Purchase Order", required=True,
        tracking=True, ondelete="restrict",
        help="Order that defines the quantities and prices the vendor "
             "committed to.")
    picking_id = fields.Many2one(
        "stock.picking", string="Receipt", tracking=True, ondelete="restrict",
        domain=[("picking_type_id.code", "=", "incoming")],
        help="Receipt whose done stock moves prove what was actually "
             "delivered. Leave empty to use every done move of the order.")
    bill_id = fields.Many2one(
        "account.move", string="Vendor Bill", required=True, tracking=True,
        ondelete="restrict",
        domain=[("move_type", "in", ["in_invoice", "in_refund"])],
        help="Vendor bill being checked. One check per bill and per company.")
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    tolerance_pct = fields.Float(
        string="Tolerance (%)", default=2.0, tracking=True,
        help="Accepted variance, in percent, on quantities and unit prices. "
             "Zero means a strict match.")
    state = fields.Selection(
        [("draft", "Draft"), ("ok", "Matched"),
         ("exception", "Exception"), ("validated", "Validated")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    line_ids = fields.One2many(
        "match.check.line", "check_id", string="Match Lines", copy=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    total_ordered = fields.Monetary(
        string="Total Ordered", currency_field="currency_id",
        compute="_compute_totals", store=True,
        help="Ordered quantity multiplied by the ordered unit price.")
    total_received = fields.Monetary(
        string="Total Received", currency_field="currency_id",
        compute="_compute_totals", store=True,
        help="Received quantity valued at the ordered unit price.")
    total_billed = fields.Monetary(
        string="Total Billed", currency_field="currency_id",
        compute="_compute_totals", store=True,
        help="Billed quantity multiplied by the billed unit price.")
    variance_amount = fields.Monetary(
        string="Variance", currency_field="currency_id",
        compute="_compute_totals", store=True,
        help="Billed total minus ordered total. Positive means the vendor "
             "bills more than was ordered.")
    exception_reason = fields.Text(
        tracking=True, copy=False,
        help="Justification required before an exception can be validated.")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('bill_company_uniq', "UNIQUE(bill_id, company_id)", "A three-way match check already exists for this vendor bill in this "
        "company. Open the existing check instead of creating a second one."),
    ]

    @api.depends("line_ids.qty_ordered", "line_ids.qty_received",
                 "line_ids.qty_billed", "line_ids.price_ordered",
                 "line_ids.price_billed")
    def _compute_totals(self):
        for check in self:
            check.total_ordered = sum(
                line.qty_ordered * line.price_ordered
                for line in check.line_ids)
            check.total_received = sum(
                line.qty_received * line.price_ordered
                for line in check.line_ids)
            check.total_billed = sum(
                line.qty_billed * line.price_billed
                for line in check.line_ids)
            check.variance_amount = (
                check.total_billed - check.total_ordered)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "match.check") or "/"
            bill_id = vals.get("bill_id")
            if bill_id:
                company_id = vals.get("company_id") or self.env.company.id
                duplicate = self.search([
                    ("bill_id", "=", bill_id),
                    ("company_id", "=", company_id),
                ], limit=1)
                if duplicate:
                    raise UserError(_(
                        "The bill \"%(bill)s\" is already checked by "
                        "\"%(check)s\".",
                        bill=duplicate.bill_id.display_name,
                        check=duplicate.name))
        return super().create(vals_list)

    @api.constrains("tolerance_pct")
    def _check_tolerance(self):
        for check in self:
            if not 0.0 <= check.tolerance_pct <= 100.0:
                raise ValidationError(_(
                    "The tolerance of the check \"%s\" must be between 0 and "
                    "100 percent.", check.name))

    def _prepare_line_values(self):
        """Collect ordered, received and billed figures, product by product."""
        self.ensure_one()
        values = {}

        def bucket(product):
            return values.setdefault(product.id, {
                "product_id": product.id,
                "qty_ordered": 0.0,
                "qty_received": 0.0,
                "qty_billed": 0.0,
                "price_ordered": 0.0,
                "price_billed": 0.0,
            })

        for line in self.purchase_id.order_line:
            if not line.product_id or line.display_type:
                continue
            data = bucket(line.product_id)
            data["qty_ordered"] += line.product_qty
            if not data["price_ordered"]:
                data["price_ordered"] = line.price_unit

        domain = [("state", "=", "done"), ("product_id", "!=", False)]
        if self.picking_id:
            domain.append(("picking_id", "=", self.picking_id.id))
        else:
            domain.append(("purchase_line_id.order_id", "=", self.purchase_id.id))
        for move in self.env["stock.move"].search(domain):
            bucket(move.product_id)["qty_received"] += move.quantity

        for line in self.bill_id.invoice_line_ids:
            if not line.product_id \
                    or line.display_type not in (False, "product"):
                continue
            data = bucket(line.product_id)
            data["qty_billed"] += line.quantity
            data["price_billed"] = line.price_unit

        return [values[key] for key in sorted(values)]

    def action_run(self):
        Line = self.env["match.check.line"]
        for check in self:
            if check.state == "validated":
                raise UserError(_(
                    "The check \"%s\" is validated: reset it to draft before "
                    "running the match again.", check.name))
            if not check.purchase_id or not check.bill_id:
                raise UserError(_(
                    "Select a purchase order and a vendor bill before running "
                    "the match."))
            values = check._prepare_line_values()
            if not values:
                raise UserError(_(
                    "The purchase order, the receipt and the vendor bill of "
                    "the check \"%s\" share no product line.", check.name))
            statuses = [Line._status(
                data["qty_ordered"], data["qty_received"],
                data["qty_billed"], data["price_ordered"],
                data["price_billed"], check.tolerance_pct)
                for data in values]
            clean = all(status == "ok" for status in statuses)
            commands = [(5, 0, 0)] + [(0, 0, data) for data in values]
            check.write({
                "line_ids": commands,
                "state": "ok" if clean else "exception",
                "exception_reason": False,
            })
            check.message_post(body=_(
                "Match run on %(count)s line(s): ordered %(ordered).2f, "
                "received %(received).2f, billed %(billed).2f.",
                count=len(values), ordered=check.total_ordered,
                received=check.total_received, billed=check.total_billed))
        return True

    def action_validate(self):
        for check in self:
            if check.state == "draft":
                raise UserError(_(
                    "Run the match on the check \"%s\" before validating it.",
                    check.name))
            if check.state == "validated":
                raise UserError(_(
                    "The check \"%s\" is already validated.", check.name))
            if check.state == "exception" \
                    and not (check.exception_reason or "").strip():
                raise UserError(_(
                    "The check \"%s\" is in exception: write an exception "
                    "reason before validating it.", check.name))
            check.write({"state": "validated"})
            check.message_post(body=_(
                "Check validated with a variance of %(variance).2f.",
                variance=check.variance_amount))
        return True

    def action_flag_exception(self, reason=None):
        for check in self:
            if check.state == "validated":
                raise UserError(_(
                    "The check \"%s\" is validated: reset it to draft before "
                    "flagging an exception.", check.name))
            text = (reason or check.exception_reason or "").strip()
            if not text:
                raise UserError(_(
                    "An exception reason is required to flag the check "
                    "\"%s\".", check.name))
            check.write({"state": "exception", "exception_reason": text})
            check.message_post(body=_(
                "Exception flagged: %s", text))
        return True

    def action_reset(self):
        for check in self:
            check.write({"state": "draft", "exception_reason": False})
            check.message_post(body=_("Check reset to draft."))
        return True


class MatchCheckLine(models.Model):
    _name = "match.check.line"
    _description = "Three-Way Match Line"
    _order = "check_id, product_id"

    check_id = fields.Many2one(
        "match.check", string="Match Check", required=True,
        ondelete="cascade", index=True)
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, index=True)
    qty_ordered = fields.Float(string="Ordered Qty", digits="Product Unit")
    qty_received = fields.Float(string="Received Qty", digits="Product Unit")
    qty_billed = fields.Float(string="Billed Qty", digits="Product Unit")
    price_ordered = fields.Monetary(
        string="Ordered Price", currency_field="currency_id")
    price_billed = fields.Monetary(
        string="Billed Price", currency_field="currency_id")
    currency_id = fields.Many2one(
        related="check_id.currency_id", store=True, readonly=True)
    status = fields.Selection(
        [("ok", "Compliant"), ("qty", "Quantity Variance"),
         ("price", "Price Variance")],
        compute="_compute_status", store=True, tracking=True,
        help="Compliant when every quantity and the unit price stay within "
             "the tolerance of the check.")

    @staticmethod
    def _status(qty_ordered, qty_received, qty_billed, price_ordered,
                price_billed, tolerance_pct):
        """Return the status of a match from raw figures.

        The quantity variance covers both the ordered/received gap and the
        received/billed gap, expressed on the ordered quantity. The price
        variance compares the billed unit price with the ordered one.
        """
        tolerance = (tolerance_pct or 0.0) / 100.0
        ordered = qty_ordered or 0.0
        received = qty_received or 0.0
        billed = qty_billed or 0.0
        if ordered:
            if abs(received - ordered) / ordered > tolerance \
                    or abs(billed - received) / ordered > tolerance:
                return "qty"
        elif received or billed:
            return "qty"
        price = price_ordered or 0.0
        if price and abs((price_billed or 0.0) - price) / price > tolerance:
            return "price"
        return "ok"

    @api.depends("qty_ordered", "qty_received", "qty_billed",
                 "price_ordered", "price_billed", "check_id.tolerance_pct")
    def _compute_status(self):
        for line in self:
            line.status = self._status(
                line.qty_ordered, line.qty_received, line.qty_billed,
                line.price_ordered, line.price_billed,
                line.check_id.tolerance_pct)
