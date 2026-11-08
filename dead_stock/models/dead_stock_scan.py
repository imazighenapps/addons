# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _


class DeadStockScan(models.Model):
    _name = "dead.stock.scan"
    _description = "Dead Stock Scan"
    _order = "create_date desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: "Scan %s" % fields.Date.context_today(self))
    date_ref = fields.Date(
        required=True, default=fields.Date.context_today)
    rule_id = fields.Many2one(
        "dead.stock.rule", string="Rule", required=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    line_ids = fields.One2many(
        "dead.stock.line", "scan_id", string="Dormant Lines")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")], default="draft")
    total_value = fields.Monetary(
        string="Locked Cash", currency_field="currency_id",
        compute="_compute_totals", store=True)
    total_carrying = fields.Monetary(
        string="Holding Cost", currency_field="currency_id",
        compute="_compute_totals", store=True)
    product_count = fields.Integer(
        string="Products", compute="_compute_totals", store=True)

    @api.depends("line_ids.value", "line_ids.carrying_cost")
    def _compute_totals(self):
        for scan in self:
            scan.total_value = sum(scan.line_ids.mapped("value"))
            scan.total_carrying = sum(
                scan.line_ids.mapped("carrying_cost"))
            scan.product_count = len(scan.line_ids)

    def _last_delivery(self, product):
        move = self.env["stock.move"].search([
            ("product_id", "=", product.id),
            ("state", "=", "done"),
            ("location_dest_id.usage", "=", "customer"),
        ], order="date desc", limit=1)
        return move.date.date() if move and move.date else False

    def action_run(self):
        self.ensure_one()
        rule = self.rule_id
        self.line_ids.unlink()
        date_ref = self.date_ref or fields.Date.context_today(self)
        domain = [
            ("qty_available", ">", 0),
            "|", ("company_id", "=", False),
            ("company_id", "=", self.company_id.id),
        ]
        if rule.category_ids:
            domain.append(("categ_id", "in", rule.category_ids.ids))
        products = self.env["product.product"].search(domain)
        if rule.warehouse_id:
            quants = self.env["stock.quant"].search([
                ("location_id", "child_of", rule.warehouse_id.id),
            ])
            products = products.filtered(
                lambda p: p in quants.mapped("product_id"))
        old_date = date_ref - timedelta(days=3650)
        Line = self.env["dead.stock.line"]
        for product in products:
            last = self._last_delivery(product)
            days_idle = (date_ref - (last or old_date)).days
            value = (product.qty_available or 0.0) \
                * (product.standard_price or 0.0)
            if days_idle < rule.slow_days:
                continue
            if value < rule.min_value:
                continue
            Line.create({
                "scan_id": self.id,
                "rule_id": rule.id,
                "product_id": product.id,
                "company_id": self.company_id.id,
                "qty_available": product.qty_available,
                "last_move_date": last or False,
                "days_idle": days_idle,
                "suggested_action": "keep",
            })
        self.state = "done"
        return {
            "type": "ir.actions.act_window",
            "name": _("Dormant Items"),
            "res_model": "dead.stock.line",
            "view_mode": "list,form",
            "domain": [("scan_id", "=", self.id)],
        }
