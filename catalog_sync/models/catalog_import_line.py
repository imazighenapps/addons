# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CatalogImportLine(models.Model):
    _name = "catalog.import.line"
    _description = "Supplier Price Line"
    _order = "import_id, id"

    name = fields.Char(compute="_compute_name", store=True)
    import_id = fields.Many2one(
        "catalog.import", string="Price List", required=True,
        ondelete="cascade")
    reference = fields.Char(required=True)
    product_id = fields.Many2one("product.product", string="Product")
    product_name = fields.Char()
    old_cost = fields.Float(string="Cost Before")
    new_cost = fields.Float(string="Cost After")
    old_price = fields.Float(string="Price Before")
    new_price = fields.Float(string="Price After")
    cost_delta = fields.Float(
        string="Cost Variation", compute="_compute_delta", store=True)
    price_delta = fields.Float(
        string="Price Variation", compute="_compute_delta", store=True)
    state = fields.Selection(
        [("matched", "Matched"), ("unmatched", "Unmatched"),
         ("applied", "Applied"), ("ignored", "Ignored")],
        default="matched", required=True, index=True)
    note = fields.Text()

    @api.depends("old_cost", "new_cost", "old_price", "new_price")
    def _compute_delta(self):
        for line in self:
            line.cost_delta = (line.new_cost or 0.0) - (line.old_cost or 0.0)
            line.price_delta = (line.new_price or 0.0) \
                - (line.old_price or 0.0)

    @api.depends("reference", "product_name")
    def _compute_name(self):
        for line in self:
            line.name = line.product_name or line.reference or ""
