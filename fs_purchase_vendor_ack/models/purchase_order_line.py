from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        orders = lines.mapped('order_id')
        if orders:
            orders._invalidate_fs_vendor_acknowledgments()
        return lines

    def write(self, vals):
        material = {
            'product_id',
            'product_qty',
            'product_uom_id',
            'date_planned',
            'price_unit',
            'taxes_id',
            'name',
            'discount',
        }
        result = super().write(vals)
        if material.intersection(vals):
            self.mapped('order_id')._invalidate_fs_vendor_acknowledgments()
        return result

    def unlink(self):
        orders = self.mapped('order_id')
        result = super().unlink()
        orders._invalidate_fs_vendor_acknowledgments()
        return result
