from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fs_delivery_promise_risk_count = fields.Integer(
        compute='_compute_fs_delivery_promise_risk_count',
    )
    fs_delivery_promise_status = fields.Selection(
        [
            ('safe', 'Safe'),
            ('at_risk', 'At Risk'),
            ('late', 'Late'),
            ('delivered_late', 'Delivered Late'),
        ],
        compute='_compute_fs_delivery_promise_status',
    )

    def _compute_fs_delivery_promise_risk_count(self):
        Risk = self.env['fs.delivery.promise.risk']
        grouped = Risk._read_group(
            [('sale_order_id', 'in', self.ids), ('status', '!=', 'safe')],
            ['sale_order_id'],
            ['__count'],
        )
        counts = {order.id: count for order, count in grouped}
        for order in self:
            order.fs_delivery_promise_risk_count = counts.get(order.id, 0)

    def _compute_fs_delivery_promise_status(self):
        Risk = self.env['fs.delivery.promise.risk']
        risks = Risk.search([('sale_order_id', 'in', self.ids)])
        by_order = {risk.sale_order_id.id: risk.status for risk in risks}
        for order in self:
            order.fs_delivery_promise_status = by_order.get(order.id, False)

    def action_fs_delivery_promise_risk(self):
        self.ensure_one()
        risk = self.env['fs.delivery.promise.risk'].search(
            [('sale_order_id', '=', self.id)], limit=1
        )
        if not risk:
            self.env['fs.delivery.promise.risk'].refresh(self)
            risk = self.env['fs.delivery.promise.risk'].search(
                [('sale_order_id', '=', self.id)], limit=1
            )
        if not risk:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery Promise Risk'),
            'res_model': 'fs.delivery.promise.risk',
            'view_mode': 'form',
            'res_id': risk.id,
        }

    def action_fs_delivery_promise_risks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery Promise Risks'),
            'res_model': 'fs.delivery.promise.risk',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', '=', self.id)],
        }
