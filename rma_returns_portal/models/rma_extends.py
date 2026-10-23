# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_returnable = fields.Boolean(string="Returnable", default=True)
    return_window_override = fields.Integer(string="Return Window Override (days)")
    refurbished_product_id = fields.Many2one(
        "product.product", string="Refurbished Product")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    rma_request_id = fields.Many2one("rma.request", string="RMA Request", copy=False)
