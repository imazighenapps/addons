# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockCard(models.Model):
    _name = "stock.card"
    _description = "Stock Card"
    _inherit = ["mail.thread"]
    _order = "date_to desc, id desc"

    name = fields.Char(default="/", required=True, copy=False, tracking=True)
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, tracking=True)
    location_id = fields.Many2one(
        "stock.location", string="Warehouse / Location", required=True,
        domain=[("usage", "=", "internal")])
    lot_id = fields.Many2one("stock.lot", string="Lot / Serial")
    date_from = fields.Date(
        required=True, default=lambda self: fields.Date.context_today(self).replace(day=1))
    date_to = fields.Date(
        required=True, default=fields.Date.context_today)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    line_ids = fields.One2many("stock.card.line", "card_id", string="Movements")
    opening_qty = fields.Float(string="Opening Qty", readonly=True)
    in_qty = fields.Float(
        string="In Qty", compute="_compute_totals", store=True)
    out_qty = fields.Float(
        string="Out Qty", compute="_compute_totals", store=True)
    closing_qty = fields.Float(
        string="Closing Qty", compute="_compute_totals", store=True)
    unit_cost = fields.Float(string="Unit Cost", default=0.0)
    opening_value = fields.Monetary(
        string="Opening Value", compute="_compute_totals", store=True,
        currency_field="currency_id")
    in_value = fields.Monetary(
        string="In Value", compute="_compute_totals", store=True,
        currency_field="currency_id")
    out_value = fields.Monetary(
        string="Out Value", compute="_compute_totals", store=True,
        currency_field="currency_id")
    closing_value = fields.Monetary(
        string="Closing Value", compute="_compute_totals", store=True,
        currency_field="currency_id")
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "stock.card") or "/"
        return super().create(vals_list)

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for card in self:
            if card.date_from > card.date_to:
                raise UserError(_("The start date must be before the end date."))

    @api.depends("line_ids.qty_in", "line_ids.qty_out", "unit_cost", "opening_qty")
    def _compute_totals(self):
        for card in self:
            card.in_qty = sum(card.line_ids.mapped("qty_in"))
            card.out_qty = sum(card.line_ids.mapped("qty_out"))
            card.closing_qty = card.opening_qty + card.in_qty - card.out_qty
            card.opening_value = card.opening_qty * card.unit_cost
            card.in_value = card.in_qty * card.unit_cost
            card.out_value = card.out_qty * card.unit_cost
            card.closing_value = card.closing_qty * card.unit_cost

    def _move_domain(self, date_from, date_to):
        self.ensure_one()
        domain = [
            ("state", "=", "done"),
            ("product_id", "=", self.product_id.id),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("company_id", "=", self.company_id.id),
        ]
        if self.lot_id:
            domain.append(("lot_id", "=", self.lot_id.id))
        return domain

    def _opening_qty(self):
        moves = self.env["stock.move"].search([
            ("state", "=", "done"),
            ("product_id", "=", self.product_id.id),
            ("date", "<", self.date_from),
            ("company_id", "=", self.company_id.id),
        ] + ([("lot_id", "=", self.lot_id.id)] if self.lot_id else []))
        total = 0.0
        for move in moves:
            qty = move.quantity or move.product_uom_qty
            if move.location_dest_id == self.location_id:
                total += qty
            if move.location_id == self.location_id:
                total -= qty
        return total

    def action_generate(self):
        for card in self:
            if not card.product_id or not card.location_id:
                raise UserError(_("Select a product and a location first."))
            card.line_ids.unlink()
            card.opening_qty = card._opening_qty()
            moves = self.env["stock.move"].search(
                card._move_domain(card.date_from, card.date_to),
                order="date, id")
            balance = card.opening_qty
            vals_list = []
            for move in moves:
                qty = move.quantity or move.product_uom_qty
                qty_in = qty if move.location_dest_id == card.location_id else 0.0
                qty_out = qty if move.location_id == card.location_id else 0.0
                if not qty_in and not qty_out:
                    continue
                balance += qty_in - qty_out
                vals_list.append({
                    "card_id": card.id,
                    "date": move.date,
                    "reference": move.reference or move.origin or _("Move %s") % move.id,
                    "partner_id": move.partner_id.id if move.partner_id else False,
                    "qty_in": qty_in,
                    "qty_out": qty_out,
                    "balance": balance,
                    "unit_cost": card.unit_cost,
                    "value": (qty_in - qty_out) * card.unit_cost,
                })
            card.write({"line_ids": [(0, 0, vals) for vals in vals_list]})
            card.message_post(body=_(
                "Stock card generated: %(in)s in, %(out)s out.",
                **{"in": card.in_qty, "out": card.out_qty}))
        return True

    def action_print(self):
        return self.env.ref(
            "stock_card_pro.action_report_stock_card").report_action(self)


class StockCardLine(models.Model):
    _name = "stock.card.line"
    _description = "Stock Card Line"
    _order = "date, id"

    card_id = fields.Many2one(
        "stock.card", required=True, ondelete="cascade", index=True)
    date = fields.Datetime(required=True)
    reference = fields.Char()
    partner_id = fields.Many2one("res.partner", string="Partner")
    qty_in = fields.Float(string="In")
    qty_out = fields.Float(string="Out")
    balance = fields.Float(string="Balance")
    unit_cost = fields.Float(string="Unit Cost")
    value = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        related="card_id.currency_id", store=True, readonly=True)
