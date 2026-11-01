# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockValReport(models.Model):
    _name = "stock.val.report"
    _description = "Stock Valuation Report"
    _inherit = ["mail.thread"]
    _order = "date_to desc, id desc"

    name = fields.Char(default="/", required=True, copy=False, tracking=True)
    date_from = fields.Date(
        required=True, tracking=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
        help="First day of the closing period, included in the report.")
    date_to = fields.Date(
        required=True, tracking=True, default=fields.Date.context_today,
        help="Last day of the closing period, included in the report.")
    location_id = fields.Many2one(
        "stock.location", string="Location",
        domain=[("usage", "=", "internal")],
        help="Leave empty to value every internal location of the company. "
             "Set a location to value the flows in and out of it only.")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    line_ids = fields.One2many(
        "stock.val.report.line", "report_id", string="Valuation Lines",
        copy=False)
    total_in_qty = fields.Float(
        string="Total In Qty", compute="_compute_totals", store=True)
    total_out_qty = fields.Float(
        string="Total Out Qty", compute="_compute_totals", store=True)
    total_value = fields.Monetary(
        string="Total Value", compute="_compute_totals", store=True,
        currency_field="currency_id",
        help="Net value of the report: the sum of the balance value of "
             "every line, at the cost captured on the line.")
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    _name_company_uniq = models.Constraint(
        "UNIQUE(name, company_id)",
        "The report reference must be unique per company.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "stock.val.report") or "/"
        return super().create(vals_list)

    def write(self, vals):
        locked = {"date_from", "date_to", "location_id", "company_id"}
        if locked & set(vals):
            for report in self:
                if report.state == "confirmed":
                    raise UserError(_(
                        "The report \"%s\" is confirmed: its period and its "
                        "location can no longer be changed. Reset it to "
                        "draft first.", report.name))
        return super().write(vals)

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for report in self:
            if report.date_from and report.date_to \
                    and report.date_from > report.date_to:
                raise ValidationError(_(
                    "The end date cannot be before the start date."))

    @api.depends("line_ids.qty_in", "line_ids.qty_out",
                 "line_ids.balance_value")
    def _compute_totals(self):
        for report in self:
            report.total_in_qty = sum(report.line_ids.mapped("qty_in"))
            report.total_out_qty = sum(report.line_ids.mapped("qty_out"))
            report.total_value = sum(report.line_ids.mapped("balance_value"))

    def _move_domain(self):
        """Done moves of the period, restricted to the location when set."""
        self.ensure_one()
        # date_to is a Date and stock.move.date is a Datetime: the upper
        # bound is the next midnight so the whole last day is included.
        domain = [
            ("state", "=", "done"),
            ("company_id", "=", self.company_id.id),
            ("date", ">=", fields.Datetime.to_datetime(self.date_from)),
            ("date", "<",
             fields.Datetime.to_datetime(self.date_to) + timedelta(days=1)),
        ]
        if self.location_id:
            domain += [
                "|",
                ("location_id", "=", self.location_id.id),
                ("location_dest_id", "=", self.location_id.id),
            ]
        return domain

    def _split_move(self, move, qty):
        """Return the (in, out) quantity of one move for this report.

        With a location, a move entering it is an inbound and a move leaving
        it is an outbound. Without a location, only the flows crossing the
        internal perimeter count: internal to internal transfers move stock
        around but do not change the valuation of the company.
        """
        self.ensure_one()
        if self.location_id:
            if move.location_id == self.location_id \
                    and move.location_dest_id == self.location_id:
                return 0.0, 0.0
            qty_in = qty if move.location_dest_id == self.location_id else 0.0
            qty_out = qty if move.location_id == self.location_id else 0.0
            return qty_in, qty_out
        source_internal = move.location_id.usage == "internal"
        dest_internal = move.location_dest_id.usage == "internal"
        if dest_internal and not source_internal:
            return qty, 0.0
        if source_internal and not dest_internal:
            return 0.0, qty
        return 0.0, 0.0

    def action_generate(self):
        for report in self:
            if report.state == "confirmed":
                raise UserError(_(
                    "The report \"%s\" is confirmed and can no longer be "
                    "regenerated. Reset it to draft first.", report.name))
            if not report.date_from or not report.date_to:
                raise UserError(_("Set the start and the end date first."))
            if report.date_from > report.date_to:
                raise UserError(_(
                    "The end date cannot be before the start date."))
            report.line_ids.unlink()
            moves = self.env["stock.move"].search(
                report._move_domain(), order="date, id")
            # Aggregate the flows per product before writing a single line.
            totals = {}
            for move in moves:
                qty = move.quantity or move.product_uom_qty
                if not qty:
                    continue
                qty_in, qty_out = report._split_move(move, qty)
                if not qty_in and not qty_out:
                    continue
                values = totals.setdefault(
                    move.product_id.id, {"qty_in": 0.0, "qty_out": 0.0})
                values["qty_in"] += qty_in
                values["qty_out"] += qty_out
            vals_list = []
            for product_id in sorted(totals):
                product = self.env["product.product"].browse(product_id)
                qty_in = totals[product_id]["qty_in"]
                qty_out = totals[product_id]["qty_out"]
                vals_list.append({
                    "report_id": report.id,
                    "product_id": product.id,
                    "qty_in": qty_in,
                    "qty_out": qty_out,
                    # The cost is captured here, once, and stored on the
                    # line: the report does not follow later cost updates.
                    "unit_cost": product.standard_price or 0.0,
                    "slow_mover": bool(
                        qty_out <= 0.0 and (qty_in - qty_out) > 0.0),
                })
            if vals_list:
                self.env["stock.val.report.line"].create(vals_list)
            report.message_post(body=_(
                "Valuation generated for the period %(start)s - %(end)s: "
                "%(count)s product(s), %(in)s in and %(out)s out.",
                start=report.date_from, end=report.date_to,
                count=len(vals_list), **{"in": report.total_in_qty,
                                         "out": report.total_out_qty}))
        return True

    def action_confirm(self):
        for report in self:
            if report.state != "draft":
                raise UserError(_("Only a draft report can be confirmed."))
            if not report.line_ids:
                raise UserError(_(
                    "Generate the valuation lines of \"%s\" before "
                    "confirming it.", report.name))
            report.state = "confirmed"
            report.message_post(body=_(
                "Report confirmed with %(count)s line(s) for a net value of "
                "%(value)s.", count=len(report.line_ids),
                value=report.total_value))
        return True

    def action_reset(self):
        for report in self:
            if report.state != "confirmed":
                raise UserError(_(
                    "Only a confirmed report can be reset to draft."))
            report.state = "draft"
            report.message_post(body=_("Report reset to draft."))
        return True


class StockValReportLine(models.Model):
    _name = "stock.val.report.line"
    _description = "Stock Valuation Report Line"
    _order = "report_id, categ_id, product_id"

    report_id = fields.Many2one(
        "stock.val.report", string="Report", required=True,
        ondelete="cascade", index=True)
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, index=True)
    categ_id = fields.Many2one(
        "product.category", string="Product Category",
        related="product_id.categ_id", store=True, readonly=True)
    qty_in = fields.Float(string="Qty In", default=0.0)
    qty_out = fields.Float(string="Qty Out", default=0.0)
    unit_cost = fields.Float(
        string="Unit Cost", compute="_compute_unit_cost", store=True,
        readonly=False, digits="Product Price",
        help="Standard cost captured when the report is generated. It is "
             "stored on the line so the report stays stable when the product "
             "cost changes afterwards.")
    value_in = fields.Monetary(
        string="Value In", compute="_compute_amounts", store=True,
        currency_field="currency_id")
    value_out = fields.Monetary(
        string="Value Out", compute="_compute_amounts", store=True,
        currency_field="currency_id")
    balance_qty = fields.Float(
        string="Balance Qty", compute="_compute_amounts", store=True)
    balance_value = fields.Monetary(
        string="Balance Value", compute="_compute_amounts", store=True,
        currency_field="currency_id",
        help="(Quantity in - quantity out) x unit cost of the line.")
    slow_mover = fields.Boolean(
        string="Slow Mover",
        help="Set when the product was received in the period but never "
             "issued. It can be adjusted by hand before the confirmation.")
    currency_id = fields.Many2one(
        related="report_id.currency_id", store=True, readonly=True)

    _report_product_uniq = models.Constraint(
        "UNIQUE(report_id, product_id)",
        "A product can only appear once per valuation report.")

    @api.depends("product_id")
    def _compute_unit_cost(self):
        for line in self:
            line.unit_cost = line.product_id.standard_price or 0.0

    @api.depends("qty_in", "qty_out", "unit_cost")
    def _compute_amounts(self):
        for line in self:
            line.balance_qty = line.qty_in - line.qty_out
            line.value_in = line.qty_in * line.unit_cost
            line.value_out = line.qty_out * line.unit_cost
            line.balance_value = line.balance_qty * line.unit_cost

    @api.constrains("qty_in", "qty_out")
    def _check_quantities(self):
        for line in self:
            if line.qty_in < 0 or line.qty_out < 0:
                raise ValidationError(_(
                    "The quantities of the line \"%s\" cannot be negative.",
                    line.product_id.display_name))

    @api.model_create_multi
    def create(self, vals_list):
        report_ids = {vals["report_id"] for vals in vals_list
                      if vals.get("report_id")}
        if report_ids:
            locked = self.env["stock.val.report"].browse(
                sorted(report_ids)).filtered(
                    lambda report: report.state == "confirmed")
            if locked:
                raise UserError(_(
                    "The report \"%s\" is confirmed: no valuation line can "
                    "be added to it.", locked[0].name))
        return super().create(vals_list)

    def write(self, vals):
        editable = {"report_id", "product_id", "qty_in", "qty_out",
                    "unit_cost", "slow_mover"}
        if editable & set(vals):
            for line in self:
                if line.report_id.state == "confirmed":
                    raise UserError(_(
                        "The report \"%s\" is confirmed: its valuation lines "
                        "can no longer be changed.", line.report_id.name))
        return super().write(vals)
