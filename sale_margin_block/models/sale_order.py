from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin_amount = fields.Monetary(
        string="Margin",
        compute="_compute_margin",
        store=True,
        currency_field="currency_id",
    )

    margin_percent = fields.Float(
        string="Margin (%)",
        compute="_compute_margin",
        store=True,
        digits=(16, 2),
    )

    @api.depends(
        "order_line.price_subtotal",
        "order_line.product_id.standard_price",
        "order_line.product_uom_qty",
    )
    def _compute_margin(self):
        for order in self:
            sale_total = 0.0
            cost_total = 0.0

            for line in order.order_line:
                sale_total += line.price_subtotal
                cost_total += (
                    line.product_id.standard_price * line.product_uom_qty
                )

            order.margin_amount = sale_total - cost_total
            order.margin_percent = (
                (order.margin_amount / sale_total) * 100
                if sale_total
                else 0.0
            )

    def action_confirm(self):
        for order in self:
            if not self.env.user.has_group(
                "sale_margin_block.group_margin_manager"
            ):
                min_margin = float(
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param(
                        "sale_margin_block.min_margin_percent", 0.0
                    )
                )

                if order.margin_percent < min_margin:
                    raise UserError(
                        (
                            "Sale Order confirmation blocked.\n\n"
                            "Margin: %.2f%%\n"
                            "Minimum allowed: %.2f%%"
                        )
                        % (order.margin_percent, min_margin)
                    )

        return super().action_confirm()
