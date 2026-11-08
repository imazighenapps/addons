# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IntercoMapping(models.Model):
    _name = "interco.mapping"
    _description = "Intercompany Product Mapping"
    _order = "rule_id, id"

    name = fields.Char(compute="_compute_name", store=True)
    rule_id = fields.Many2one(
        "interco.rule", string="Rule", required=True, ondelete="cascade")
    source_product_id = fields.Many2one(
        "product.product", string="Sold Product", required=True)
    target_product_id = fields.Many2one(
        "product.product", string="Bought Product", required=True)
    price_unit = fields.Float(
        string="Imposed Price",
        help="Leave empty to let the price policy of the rule decide.")
    active = fields.Boolean(default=True)
    note = fields.Text()

    _rule_source_uniq = models.Constraint(
        "unique(rule_id, source_product_id)",
        "This product is already mapped in the rule.")

    @api.depends("source_product_id", "target_product_id")
    def _compute_name(self):
        for mapping in self:
            mapping.name = "%s -> %s" % (
                mapping.source_product_id.display_name or "",
                mapping.target_product_id.display_name or "")
