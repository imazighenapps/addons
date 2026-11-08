# -*- coding: utf-8 -*-
from odoo import fields, models


class CatalogMarginRule(models.Model):
    _name = "catalog.margin.rule"
    _description = "Catalog Margin Rule"
    _order = "category_id, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    category_id = fields.Many2one(
        "product.category", string="Product Category",
        help="Leave empty for the generic rule of the company.")
    margin_rate = fields.Float(
        string="Margin (%)", default=30.0, required=True)
    round_to = fields.Float(
        string="Rounding Step", default=0.01,
        help="Round the computed sale price to this step. Zero disables "
             "the rounding.")
    apply_sale_price = fields.Boolean(
        string="Update Sale Price", default=True,
        help="Uncheck to update the cost only and keep the current sale "
             "price.")
    active = fields.Boolean(default=True)
    note = fields.Text()

    _sql_constraints = [
        ('company_category_uniq', "unique(company_id, category_id)", "A margin rule already exists for this category and company."),
    ]

    def _sale_price(self, cost):
        self.ensure_one()
        price = (cost or 0.0) * (1.0 + (self.margin_rate or 0.0) / 100.0)
        step = self.round_to or 0.0
        if step:
            price = round(price / step) * step
        return round(price, 2)
