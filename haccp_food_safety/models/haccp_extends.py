# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allergen_ids = fields.Many2many(
        "haccp.allergen", "product_template_haccp_allergen_rel",
        "template_id", "allergen_id", string="Contains Allergens")
    may_contain_ids = fields.Many2many(
        "haccp.allergen", "product_template_haccp_traces_rel",
        "template_id", "allergen_id", string="May Contain Traces")


class HaccpWithdrawal(models.TransientModel):
    _name = "haccp.withdrawal"
    _description = "HACCP Withdrawal Assistant"

    lot_ids = fields.Many2many("stock.lot", string="Lots to Withdraw")
    customers_text = fields.Text(string="Delivered Customers", readonly=True)

    @api.onchange("lot_ids")
    def _onchange_lots(self):
        for wiz in self:
            partners = self.env["stock.move.line"].search_read(
                [("lot_id", "in", wiz.lot_ids.ids), ("picking_id.picking_type_id.code", "=", "outgoing")],
                ["picking_id", "qty_product_uom"])
            lines = set()
            for ml in partners:
                lines.add("%s x %s" % (ml["picking_id"][1] if ml["picking_id"] else "?", ml["qty_product_uom"]))
            wiz.customers_text = "\n".join(sorted(lines)) or "No outgoing delivery found."
