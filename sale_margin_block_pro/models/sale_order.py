from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin_percent = fields.Float(
        compute="_compute_margin",
        store=True,
        digits=(16, 2)
    )

    @api.depends(
        "order_line.price_subtotal",
        "order_line.product_id.standard_price",
        "order_line.product_uom_qty"
    )
    def _compute_margin(self):
        for order in self:
            sale_total = sum(order.order_line.mapped("price_subtotal"))
            cost_total = sum(
                l.product_id.standard_price * l.product_uom_qty
                for l in order.order_line
            )
            margin = sale_total - cost_total
            order.margin_percent = (
                (margin / sale_total) * 100 if sale_total else 0.0
            )

    def _get_min_margin_rule(self):
        self.ensure_one()

        Rule = self.env["sale.margin.rule"]

        # 1️⃣ Product
        for line in self.order_line:
            rule = Rule.search([
                ("product_id", "=", line.product_id.id),
                ("active", "=", True)
            ], limit=1)
            if rule:
                return rule.min_margin_percent

        # 2️⃣ Category
        for line in self.order_line:
            if line.product_id.categ_id:
                rule = Rule.search([
                    ("categ_id", "=", line.product_id.categ_id.id),
                    ("active", "=", True)
                ], limit=1)
                if rule:
                    return rule.min_margin_percent

        # 3️⃣ Customer
        rule = Rule.search([
            ("partner_id", "=", self.partner_id.id),
            ("active", "=", True)
        ], limit=1)
        if rule:
            return rule.min_margin_percent

        # 4️⃣ Global
        return float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_margin_block_pro.min_margin_percent", 0.0
            )
        )

    def action_confirm(self):
        for order in self:
            if not self.env.user.has_group(
                "sale_margin_block_pro.group_margin_manager"
            ):
                min_margin = order._get_min_margin_rule()

                if order.margin_percent < min_margin:
                    raise UserError(
                        (
                            "Confirmation blocked.\n\n"
                            "Margin: %.2f%%\n"
                            "Required: %.2f%%"
                        )
                        % (order.margin_percent, min_margin)
                    )
        return super().action_confirm()
