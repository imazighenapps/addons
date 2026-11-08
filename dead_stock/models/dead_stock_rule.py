# -*- coding: utf-8 -*-
from odoo import fields, models


class DeadStockRule(models.Model):
    _name = "dead.stock.rule"
    _description = "Dead Stock Rule"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    warehouse_id = fields.Many2one(
        "stock.location", string="Warehouse Location",
        domain=[("usage", "=", "internal")])
    category_ids = fields.Many2many(
        "product.category", string="Categories")
    slow_days = fields.Integer(
        string="Idle Days", default=90, required=True,
        help="Days without a customer delivery before a product is dormant.")
    carrying_rate = fields.Float(
        string="Carrying Rate (%)", default=20.0,
        help="Annual percentage of the stock value used to compute the cost "
             "of holding.")
    min_value = fields.Monetary(
        string="Minimum Value", currency_field="currency_id",
        help="Ignore dormant stock below this value.")
    active = fields.Boolean(default=True)
    note = fields.Text()

    _sql_constraints = [
        ('company_name_uniq', "unique(company_id, warehouse_id, name)", "A dead stock rule with this name already exists."),
    ]
