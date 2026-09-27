from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fs_delivery_promise_risk_count = fields.Integer(compute='_compute_fs_delivery_promise_risk_count')

    @api.depends('sale_id')
    def _compute_fs_delivery_promise_risk_count(self):
        Risk = self.env['fs.delivery.promise.risk']
        sale_orders = self.mapped('sale_id')
        data = Risk._read_group(
            [('sale_order_id', 'in', sale_orders.ids), ('status', '!=', 'safe')],
            ['sale_order_id'],
            ['__count'],
        )
        counts = {order.id: count for order, count in data}
        for picking in self:
            picking.fs_delivery_promise_risk_count = counts.get(picking.sale_id.id, 0)

    def action_fs_delivery_promise_risks(self):
        self.ensure_one()
        if not self.sale_id:
            raise UserError(_('This transfer is not linked to a sales order.'))
        return self.sale_id.action_fs_delivery_promise_risks()
