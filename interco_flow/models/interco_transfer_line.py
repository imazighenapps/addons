# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IntercoTransferLine(models.Model):
    _name = "interco.transfer.line"
    _description = "Intercompany Transfer Line"
    _order = "transfer_id, id"

    name = fields.Char(compute="_compute_name", store=True)
    transfer_id = fields.Many2one(
        "interco.transfer", string="Transfer", required=True,
        ondelete="cascade")
    source_product_id = fields.Many2one(
        "product.product", string="Sold Product", required=True)
    target_product_id = fields.Many2one(
        "product.product", string="Bought Product", required=True)
    product_qty = fields.Float(string="Quantity", default=1.0, required=True)
    price_unit = fields.Float(string="Transfer Price", required=True)
    subtotal = fields.Float(
        string="Purchase Subtotal", compute="_compute_subtotal", store=True)
    subtotal_sale = fields.Float(string="Sale Subtotal")
    margin = fields.Float(
        string="Line Margin", compute="_compute_subtotal", store=True)
    note = fields.Text()

    @api.depends("product_qty", "price_unit", "subtotal_sale")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (line.product_qty or 0.0) \
                * (line.price_unit or 0.0)
            line.margin = (line.subtotal_sale or 0.0) - line.subtotal

    @api.depends("source_product_id", "target_product_id")
    def _compute_name(self):
        for line in self:
            line.name = "%s -> %s" % (
                line.source_product_id.display_name or "",
                line.target_product_id.display_name or "")
