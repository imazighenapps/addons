from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models


class CustomerOrderSnapshotWizard(models.TransientModel):
    _name = 'fs.customer.order.snapshot.wizard'
    _description = 'Customer Order Snapshot'

    sale_order_id = fields.Many2one('sale.order', required=True, readonly=True)
    partner_id = fields.Many2one('res.partner', required=True, readonly=True)
    product_id = fields.Many2one('product.product')
    line_ids = fields.One2many('fs.customer.order.snapshot.line', 'wizard_id', copy=False)

    def populate_lines(self):
        self.ensure_one()
        config = self.env['fs.customer.order.snapshot.config'].sudo().search([
            ('company_id', '=', self.sale_order_id.company_id.id)
        ], limit=1)
        lookback_days = config.lookback_days if config else 365
        max_orders = config.max_orders if config else 5
        self.line_ids.unlink()
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('company_id', '=', self.sale_order_id.company_id.id),
            ('state', 'in', ('sale', 'done')),
            ('id', '!=', self.sale_order_id.id),
            ('date_order', '>=', fields.Datetime.now() - timedelta(days=lookback_days)),
        ]
        orders = self.env['sale.order'].search(domain, order='date_order desc', limit=max_orders)
        vals = []
        include_prices = config.include_prices if config else True
        include_discounts = config.include_discounts if config else True
        for order in orders:
            if self.product_id:
                lines = order.order_line.filtered(lambda line: line.product_id == self.product_id)
                if not lines:
                    continue
                grouped_lines = [(self.product_id, lines)]
            else:
                # Without a product filter, expose a compact product-level snapshot of the
                # recent orders instead of showing empty product columns.
                grouped = defaultdict(lambda: self.env['sale.order.line'])
                for line in order.order_line.filtered(lambda line: line.product_id):
                    grouped[line.product_id] |= line
                grouped_lines = list(grouped.items())
            for product, lines in grouped_lines:
                qty = sum(lines.mapped('product_uom_qty'))
                unit = lines[0].price_unit if lines else 0.0
                discount = lines[0].discount if lines else 0.0
                vals.append((0, 0, {
                    'order_id': order.id,
                    'date_order': order.date_order,
                    'order_total': order.amount_total,
                    'product_id': product.id,
                    'quantity': qty,
                    'unit_price': unit if include_prices else 0.0,
                    'discount': discount if include_discounts else 0.0,
                }))
        self.line_ids = vals
        return True


class CustomerOrderSnapshotLine(models.TransientModel):
    _name = 'fs.customer.order.snapshot.line'
    _description = 'Customer Order Snapshot Line'

    wizard_id = fields.Many2one('fs.customer.order.snapshot.wizard', required=True, ondelete='cascade')
    order_id = fields.Many2one('sale.order', readonly=True)
    date_order = fields.Datetime(readonly=True)
    order_total = fields.Monetary(readonly=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='wizard_id.sale_order_id.currency_id')
    product_id = fields.Many2one('product.product', readonly=True)
    quantity = fields.Float(readonly=True)
    unit_price = fields.Float(readonly=True)
    discount = fields.Float(readonly=True)
