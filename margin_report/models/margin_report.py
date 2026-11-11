# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MarginBook(models.Model):
    _name = "margin.book"
    _description = "Order Margin Sheet"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(
        required=True, tracking=True,
        help="Name of the margin sheet, usually the order reference.")
    order_ref = fields.Char(
        string="Order Reference", required=True, tracking=True,
        help="Reference of the realised sale this margin sheet covers.")
    partner_id = fields.Many2one("res.partner", string="Customer")
    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", tracking=True,
        default=lambda self: self.env.user)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    target_rate = fields.Float(
        string="Target Margin (%)", default=25.0, tracking=True,
        help="Minimum margin rate the sheet should reach.")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    line_ids = fields.One2many(
        "margin.book.line", "book_id", string="Margin Lines", copy=True)
    line_count = fields.Integer(
        string="Lines", compute="_compute_line_count", store=True,
        help="Number of lines of the sheet.")
    total_revenue = fields.Monetary(
        string="Revenue", currency_field="currency_id",
        compute="_compute_totals", store=True)
    total_cost = fields.Monetary(
        string="Cost", currency_field="currency_id",
        compute="_compute_totals", store=True)
    total_margin = fields.Monetary(
        string="Net Margin", currency_field="currency_id",
        compute="_compute_totals", store=True)
    margin_rate = fields.Float(
        string="Margin Rate (%)", compute="_compute_totals", store=True,
        help="Net margin as a percentage of the revenue.")
    is_below_target = fields.Boolean(
        string="Under Target", compute="_compute_is_below_target",
        store=True, help="Set when the margin rate is below the target "
             "margin of the sheet.")
    confirmed_on = fields.Date(
        string="Confirmed On", readonly=True, copy=False,
        help="Date the sheet was confirmed and frozen.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.amount_revenue",
                 "line_ids.amount_cost")
    def _compute_line_count(self):
        for book in self:
            book.line_count = len(book.line_ids)

    @api.depends("line_ids.amount_revenue", "line_ids.amount_cost")
    def _compute_totals(self):
        for book in self:
            revenue = sum(book.line_ids.mapped("amount_revenue"))
            cost = sum(book.line_ids.mapped("amount_cost"))
            book.total_revenue = revenue
            book.total_cost = cost
            book.total_margin = revenue - cost
            book.margin_rate = (
                (revenue - cost) / revenue * 100.0 if revenue else 0.0)

    @api.depends("total_margin", "total_revenue", "target_rate")
    def _compute_is_below_target(self):
        for book in self:
            if book.total_revenue:
                book.is_below_target = (
                    book.margin_rate < book.target_rate)
            else:
                book.is_below_target = False

    @api.constrains("target_rate")
    def _check_target_rate(self):
        for book in self:
            if book.target_rate < 0 or book.target_rate > 100:
                raise ValidationError(_(
                    "The target margin of %s must be between 0 and 100.",
                    book.name))

    @api.constrains("order_ref", "company_id")
    def _check_order_ref_unique(self):
        for book in self:
            if book.order_ref and book.company_id:
                dup = self.search_count([
                    ("order_ref", "=", book.order_ref),
                    ("company_id", "=", book.company_id.id),
                    ("id", "!=", book.id),
                ])
                if dup:
                    raise ValidationError(_(
                        "The order reference %s must be unique per company.",
                        book.order_ref))

    def action_confirm(self):
        for book in self:
            if book.state != "draft":
                raise UserError(_("Only a draft sheet can be confirmed."))
            if not book.line_ids:
                raise UserError(_(
                    "Add at least one margin line before confirming the "
                    "sheet %s.", book.name))
            book.write({
                "state": "confirmed",
                "confirmed_on": fields.Date.context_today(book),
            })
            book.message_post(body=_(
                "Margin sheet frozen: %(rate).2f%% on %(revenue)s of "
                "revenue, margin %(margin)s.",
                rate=book.margin_rate, revenue=book.total_revenue,
                margin=book.total_margin))
        return True

    def action_reset(self):
        for book in self:
            if book.state != "confirmed":
                raise UserError(_("Only a confirmed sheet can be opened."))
            book.state = "draft"
            book.message_post(body=_("Margin sheet reopened in draft."))
        return True


class MarginBookLine(models.Model):
    _name = "margin.book.line"
    _description = "Order Margin Line"
    _order = "book_id, sequence, id"

    book_id = fields.Many2one(
        "margin.book", string="Margin Sheet", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    description = fields.Char(required=True)
    quantity = fields.Float(default=1.0, required=True)
    sell_price = fields.Monetary(
        string="Selling Price", required=True,
        help="Price actually sold to the customer, per unit.")
    unit_cost = fields.Monetary(
        string="Unit Cost", default=0.0, required=True,
        help="Cost actually incurred, per unit.")
    amount_revenue = fields.Monetary(
        string="Revenue", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    amount_cost = fields.Monetary(
        string="Cost", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    line_margin = fields.Monetary(
        string="Margin", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    line_rate = fields.Float(
        string="Margin (%)", compute="_compute_amounts", store=True,
        help="Margin as a percentage of the line revenue.")
    currency_id = fields.Many2one(
        related="book_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(
        related="book_id.company_id", store=True, readonly=True)

    @api.depends("quantity", "sell_price", "unit_cost")
    def _compute_amounts(self):
        for line in self:
            qty = line.quantity or 0.0
            line.amount_revenue = (line.sell_price or 0.0) * qty
            line.amount_cost = (line.unit_cost or 0.0) * qty
            line.line_margin = line.amount_revenue - line.amount_cost
            line.line_rate = (
                line.line_margin / line.amount_revenue * 100.0
                if line.amount_revenue else 0.0)

    @api.constrains("sell_price", "unit_cost", "quantity")
    def _check_amounts(self):
        for line in self:
            if line.sell_price < 0 or line.unit_cost < 0:
                raise ValidationError(_(
                    "The selling price and the unit cost of \"%s\" "
                    "cannot be negative.", line.description))
            if line.quantity <= 0:
                raise ValidationError(_(
                    "The quantity of \"%s\" must be above zero.",
                    line.description))

    @api.model_create_multi
    def create(self, vals_list):
        book_ids = {vals["book_id"] for vals in vals_list
                    if vals.get("book_id")}
        if book_ids:
            confirmed = self.env["margin.book"].browse(
                sorted(book_ids)).filtered(
                    lambda book: book.state == "confirmed")
            if confirmed:
                raise UserError(_(
                    "The margin sheet %s is confirmed: no line can be "
                    "added to it.", confirmed[0].name))
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            if line.book_id.state == "confirmed":
                raise UserError(_(
                    "The margin sheet %s is confirmed: its lines can no "
                    "longer be changed.", line.book_id.name))
        return super().write(vals)
