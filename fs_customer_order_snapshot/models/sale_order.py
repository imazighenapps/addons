from collections import defaultdict
from datetime import timedelta

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fs_snapshot_order_count = fields.Integer(compute='_compute_fs_snapshot')
    fs_snapshot_last_order_date = fields.Datetime(compute='_compute_fs_snapshot')
    fs_snapshot_last_order_name = fields.Char(compute='_compute_fs_snapshot')
    fs_snapshot_last_order_amount = fields.Monetary(
        compute='_compute_fs_snapshot',
        currency_field='currency_id',
    )
    fs_snapshot_average_interval = fields.Float(compute='_compute_fs_snapshot')
    fs_snapshot_last_product_id = fields.Many2one('product.product', compute='_compute_fs_snapshot')
    fs_snapshot_last_product_qty = fields.Float(compute='_compute_fs_snapshot')
    fs_snapshot_last_product_unit_price = fields.Float(compute='_compute_fs_snapshot')
    fs_snapshot_last_product_discount = fields.Float(compute='_compute_fs_snapshot')

    @api.depends('partner_id', 'company_id', 'date_order')
    def _compute_fs_snapshot(self):
        if not self:
            return

        configs = self.env['fs.customer.order.snapshot.config'].sudo().search([
            ('company_id', 'in', self.mapped('company_id').ids)
        ])
        config_by_company = {config.company_id.id: config for config in configs}
        grouped = defaultdict(lambda: self.env['sale.order'])

        # One query per company instead of one query per current order.
        for company in self.mapped('company_id'):
            company_orders = self.filtered(lambda order: order.company_id == company and order.partner_id)
            if not company_orders:
                continue
            config = config_by_company.get(company.id)
            lookback = config.lookback_days if config else 365
            max_orders = config.max_orders if config else 5
            boundary = fields.Datetime.now() - timedelta(days=lookback)
            orders = self.env['sale.order'].search([
                ('partner_id', 'in', company_orders.mapped('partner_id').ids),
                ('company_id', '=', company.id),
                ('state', 'in', ('sale', 'done')),
                ('date_order', '>=', boundary),
            ], order='partner_id, date_order desc, id desc')
            buckets = defaultdict(list)
            for order in orders:
                buckets[order.partner_id.id].append(order)
            for partner_id, partner_orders in buckets.items():
                grouped[(company.id, partner_id)] = self.env['sale.order'].browse(
                    [o.id for o in partner_orders[:max_orders + 1]]
                ).sorted(key=lambda o: (o.date_order, o.id), reverse=True)

        for order in self:
            if not order.partner_id:
                order.fs_snapshot_order_count = 0
                order.fs_snapshot_last_order_date = False
                order.fs_snapshot_last_order_name = False
                order.fs_snapshot_last_order_amount = 0.0
                order.fs_snapshot_average_interval = 0.0
                order.fs_snapshot_last_product_id = False
                order.fs_snapshot_last_product_qty = 0.0
                order.fs_snapshot_last_product_unit_price = 0.0
                order.fs_snapshot_last_product_discount = 0.0
                continue

            config = config_by_company.get(order.company_id.id)
            max_orders = config.max_orders if config else 5
            orders = grouped.get((order.company_id.id, order.partner_id.id), self.env['sale.order']).filtered(
                lambda candidate: candidate.id != order.id
            )[:max_orders]
            dates = orders.mapped('date_order')
            intervals = [
                (dates[index] - dates[index + 1]).total_seconds() / 86400.0
                for index in range(len(dates) - 1)
            ]
            last = orders[:1]
            order.fs_snapshot_order_count = len(orders)
            order.fs_snapshot_last_order_date = last.date_order if last else False
            order.fs_snapshot_last_order_name = last.name if last else False
            order.fs_snapshot_last_order_amount = last.amount_total if last else 0.0
            order.fs_snapshot_average_interval = (
                sum(intervals) / len(intervals) if intervals else 0.0
            )
            product_line = (last.order_line.filtered(lambda line: line.product_id)[:1] if last else self.env['sale.order.line'])
            order.fs_snapshot_last_product_id = product_line.product_id if product_line else False
            order.fs_snapshot_last_product_qty = product_line.product_uom_qty if product_line else 0.0
            order.fs_snapshot_last_product_unit_price = product_line.price_unit if product_line and (config.include_prices if config else True) else 0.0
            order.fs_snapshot_last_product_discount = product_line.discount if product_line and (config.include_discounts if config else True) else 0.0

    def action_fs_customer_snapshot(self):
        self.ensure_one()
        if not self.partner_id:
            return False
        wizard = self.env['fs.customer.order.snapshot.wizard'].create({
            'sale_order_id': self.id,
            'partner_id': self.partner_id.id,
        })
        wizard.populate_lines()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fs.customer.order.snapshot.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
            'name': _('Customer Order Snapshot'),
        }
