# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class DeadStockLine(models.Model):
    _name = "dead.stock.line"
    _description = "Dormant Stock Line"
    _order = "value desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    scan_id = fields.Many2one(
        "dead.stock.scan", string="Scan", required=True,
        ondelete="cascade")
    rule_id = fields.Many2one("dead.stock.rule", string="Rule")
    product_id = fields.Many2one(
        "product.product", string="Product", required=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    qty_available = fields.Float(string="Quantity")
    value = fields.Monetary(
        string="Stock Value", currency_field="currency_id",
        compute="_compute_value", store=True)
    last_move_date = fields.Date(string="Last Delivery")
    days_idle = fields.Integer(string="Idle Days")
    carrying_cost = fields.Monetary(
        string="Holding Cost", currency_field="currency_id",
        compute="_compute_value", store=True)
    suggested_action = fields.Selection(
        [("discount", "Discount"), ("bundle", "Bundle"),
         ("return", "Return to Supplier"), ("scrap", "Scrap"),
         ("keep", "Keep")],
        default="keep", required=True)
    state = fields.Selection(
        [("open", "Open"), ("actioned", "Actioned"), ("ignored", "Ignored")],
        default="open", required=True, index=True)
    note = fields.Text()

    @api.depends("product_id", "qty_available", "days_idle", "rule_id",
                 "rule_id.carrying_rate")
    def _compute_value(self):
        for line in self:
            price = line.product_id.standard_price or 0.0
            line.value = (line.qty_available or 0.0) * price
            rate = line.rule_id.carrying_rate or 0.0
            line.carrying_cost = line.value * (rate / 100.0) \
                * (line.days_idle or 0) / 365.0

    @api.depends("product_id")
    def _compute_name(self):
        for line in self:
            code = line.product_id.default_code
            name = line.product_id.name
            line.name = ("%s %s" % (code, name)).strip() if code \
                else (name or _("Dormant stock"))

    def action_actioned(self):
        for line in self:
            line.state = "actioned"
        return True

    def action_ignore(self):
        for line in self:
            line.state = "ignored"
        return True

    def action_reopen(self):
        for line in self:
            line.state = "open"
        return True
