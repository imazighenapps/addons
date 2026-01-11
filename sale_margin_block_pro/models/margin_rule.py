from odoo import models, fields

class SaleMarginRule(models.Model):
    _name = "sale.margin.rule"
    _description = "Sale Margin Rule"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)

    min_margin_percent = fields.Float(
        string="Minimum Margin (%)",
        required=True
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        domain="[('customer_rank','>',0)]"
    )

    product_id = fields.Many2one(
        "product.product",
        string="Product"
    )

    categ_id = fields.Many2one(
        "product.category",
        string="Product Category"
    )

    active = fields.Boolean(default=True)
