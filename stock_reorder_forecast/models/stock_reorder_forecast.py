# -*- coding: utf-8 -*-
import math
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockReorderSuggestion(models.Model):
    _name = "stock.reorder.suggestion"
    _description = "Reorder Suggestion"
    _order = "suggested_qty desc, id desc"

    product_id = fields.Many2one(
        "product.product", string="Product", required=True, index=True,
        ondelete="cascade")
    location_id = fields.Many2one(
        "stock.location", string="Location", required=True, index=True)
    date = fields.Date(default=fields.Date.context_today, index=True)
    lookback_days = fields.Integer(default=90)
    horizon_days = fields.Integer(default=30)
    avg_daily = fields.Float(string="Average Daily Issue", digits=(16, 3))
    qty_available = fields.Float(string="On Hand", digits=(16, 3))
    incoming_qty = fields.Float(string="Incoming", digits=(16, 3))
    suggested_qty = fields.Float(string="Suggested Quantity", digits=(16, 3))
    state = fields.Selection(
        [("open", "Open"), ("ordered", "Ordered"), ("ignored", "Ignored")],
        default="open", required=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model
    def _suggested_quantity(self, avg_daily, horizon_days, on_hand, incoming):
        needed = (avg_daily or 0.0) * (horizon_days or 0) - (on_hand or 0.0) \
            - (incoming or 0.0)
        if needed <= 0:
            return 0.0
        return float(math.ceil(round(needed, 3)))

    def action_ordered(self):
        for suggestion in self:
            if suggestion.state != "open":
                raise UserError(_("Only an open suggestion can be marked ordered."))
            suggestion.state = "ordered"
        return True

    def action_ignore(self):
        for suggestion in self:
            if suggestion.state == "ignored":
                raise UserError(_("This suggestion is already ignored."))
            suggestion.state = "ignored"
        return True

    def action_reopen(self):
        for suggestion in self:
            if suggestion.state != "ignored":
                raise UserError(_("Only an ignored suggestion can be reopened."))
            suggestion.state = "open"
        return True


class StockReorderForecast(models.TransientModel):
    _name = "stock.reorder.forecast"
    _description = "Reorder Forecast"

    lookback_days = fields.Integer(
        string="Lookback (days)", default=90, required=True,
        help="Window used to compute the average daily issue.")
    horizon_days = fields.Integer(
        string="Cover (days)", default=30, required=True,
        help="Number of days of consumption the suggestion must cover.")
    location_id = fields.Many2one(
        "stock.location", string="Location", required=True,
        domain=[("usage", "=", "internal")])
    category_id = fields.Many2one(
        "product.category", string="Product Category")
    only_needed = fields.Boolean(
        string="Only Products To Reorder", default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)

    @api.model
    def _default_location(self):
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1)
        return warehouse.lot_stock_id

    @api.onchange("company_id")
    def _onchange_company(self):
        self.location_id = self._default_location()

    def _incoming_qty(self, product, location):
        moves = self.env["stock.move"].search([
            ("product_id", "=", product.id),
            ("location_dest_id", "=", location.id),
            ("state", "in", ("confirmed", "assigned", "waiting")),
        ])
        return sum(moves.mapped("product_uom_qty"))

    def _outgoing_qty(self, product, location, start):
        moves = self.env["stock.move"].search([
            ("product_id", "=", product.id),
            ("location_id", "=", location.id),
            ("state", "=", "done"),
            ("date", ">=", start),
        ])
        return sum(moves.mapped("product_uom_qty"))

    def action_run(self):
        self.ensure_one()
        if self.lookback_days <= 0:
            raise UserError(_("The lookback window must be positive."))
        if self.horizon_days <= 0:
            raise UserError(_("The cover period must be positive."))
        location = self.location_id
        start = fields.Date.context_today(self) - timedelta(
            days=self.lookback_days)
        domain = [("type", "in", ("product", "consu")), ("active", "=", True)]
        if self.category_id:
            domain.append(("categ_id", "child_of", self.category_id.id))
        products = self.env["product.product"].search(domain)
        Suggestion = self.env["stock.reorder.suggestion"]
        created = Suggestion
        for product in products:
            issued = self._outgoing_qty(product, location, start)
            avg_daily = issued / float(self.lookback_days)
            on_hand = product.with_context(
                location=location.id).qty_available
            incoming = self._incoming_qty(product, location)
            suggested = Suggestion._suggested_quantity(
                avg_daily, self.horizon_days, on_hand, incoming)
            if suggested <= 0 and self.only_needed:
                continue
            values = {
                "product_id": product.id,
                "location_id": location.id,
                "lookback_days": self.lookback_days,
                "horizon_days": self.horizon_days,
                "avg_daily": avg_daily,
                "qty_available": on_hand,
                "incoming_qty": incoming,
                "suggested_qty": suggested,
                "company_id": self.company_id.id,
            }
            existing = Suggestion.search([
                ("product_id", "=", product.id),
                ("location_id", "=", location.id),
                ("state", "=", "open"),
            ], limit=1)
            if existing:
                existing.write(values)
                created |= existing
            else:
                created |= Suggestion.create(values)
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_reorder_forecast.action_stock_reorder_suggestion")
        if created:
            action["domain"] = [("id", "in", created.ids)]
        return action
