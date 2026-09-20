from odoo import api, models, _


class SmartOperationsImpactEngine(models.AbstractModel):
    _name = 'smart.operations.impact.engine'
    _description = 'Business Impact Engine'

    @api.model
    def analyze(self, record):
        result = {
            'business_impact': 0.0,
            'sales_revenue': 0.0,
            'purchase_value': 0.0,
            'impact_records': {
                'customer': {}, 'sales_order': {}, 'delivery': {},
                'manufacturing': {}, 'purchase': {},
            },
            'customers': set(),
            'orders': set(),
            'deliveries': set(),
            'manufacturing': set(),
            'purchases': set(),
            'dependency_count': 0,
            'quantity': 0.0,
            'path': [],
            'root_cause': record,
            '_seen': set(),
        }
        if not record or not record.exists():
            return result

        handlers = {
            'sale.order': self._from_sale_order,
            'stock.picking': self._from_picking,
            'stock.move': self._from_move,
            'mrp.production': self._from_manufacturing,
            'purchase.order': self._from_purchase,
            'purchase.order.line': self._from_purchase_line,
            'account.move': self._from_account_move,
            'crm.lead': self._from_crm,
        }
        handler = handlers.get(record._name)
        if handler:
            handler(record, result)
        else:
            self._add_record_facts(record, result)

        result['dependency_count'] = (
            len(result['deliveries'])
            + len(result['manufacturing'])
            + len(result['purchases'])
        )
        result['business_impact'] = result['sales_revenue'] if result['sales_revenue'] else result['purchase_value']
        result['path'] = self._unique_path(result['path'])
        result.pop('_seen', None)
        return result

    def _mark_seen(self, record, result):
        key = (record._name, record.id)
        if key in result['_seen']:
            return False
        result['_seen'].add(key)
        return True

    def _add_impact_record(self, relation_type, record, result, quantity=0.0, monetary_value=0.0):
        if not record or not record.exists():
            return
        result['impact_records'].setdefault(relation_type, {})[record.id] = {
            'record': record,
            'quantity': quantity or 0.0,
            'monetary_value': monetary_value or 0.0,
        }

    def _add_record_facts(self, record, result):
        if not self._mark_seen(record, result):
            return False
        result['path'].append(_('%s: %s') % (record._description or record._name, record.display_name))
        if record._name in ('sale.order', 'crm.lead') and 'partner_id' in record._fields and record.partner_id:
            result['customers'].add(record.partner_id.id)
            self._add_impact_record('customer', record.partner_id, result)
        if record._name == 'account.move' and record.move_type in ('out_invoice', 'out_refund') and record.partner_id:
            result['customers'].add(record.partner_id.id)
        if record._name == 'sale.order' and 'amount_total' in record._fields:
            amount = record.amount_total or 0.0
            result['sales_revenue'] += amount
            self._add_impact_record('sales_order', record, result, monetary_value=amount)
        elif record._name == 'crm.lead' and 'expected_revenue' in record._fields:
            result['sales_revenue'] += record.expected_revenue or 0.0
        elif record._name == 'account.move' and 'amount_residual' in record._fields:
            result['business_impact'] += record.amount_residual or 0.0
        return True

    def _from_sale_order(self, order, result):
        if not self._add_record_facts(order, result):
            return
        result['orders'].add(order.id)
        if 'picking_ids' in order._fields:
            pickings = order.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
            for picking in pickings[:50]:
                self._from_picking(picking, result)

    def _from_picking(self, picking, result):
        if not self._add_record_facts(picking, result):
            return
        result['deliveries'].add(picking.id)
        self._add_impact_record('delivery', picking, result)
        if 'sale_id' in picking._fields and picking.sale_id:
            self._from_sale_order(picking.sale_id, result)
        for move in picking.move_ids.filtered(lambda m: m.state not in ('done', 'cancel'))[:50]:
            self._from_move(move, result)

    def _from_move(self, move, result):
        if not self._add_record_facts(move, result):
            return
        move_qty = max(move.product_uom_qty or 0.0, 0.0)
        result['quantity'] += move_qty
        if 'sale_line_id' in move._fields and move.sale_line_id:
            self._from_sale_order(move.sale_line_id.order_id, result)
        if 'raw_material_production_id' in move._fields and move.raw_material_production_id:
            self._from_manufacturing(move.raw_material_production_id, result)
        if 'production_id' in move._fields and move.production_id:
            self._from_manufacturing(move.production_id, result)
        if 'purchase_line_id' in move._fields and move.purchase_line_id:
            self._from_purchase_line(move.purchase_line_id, result)

    def _from_manufacturing(self, mo, result):
        if not self._add_record_facts(mo, result):
            return
        result['manufacturing'].add(mo.id)
        self._add_impact_record('manufacturing', mo, result, quantity=max((mo.product_qty or 0.0) - (mo.qty_produced or 0.0), 0.0))
        result['quantity'] += max((mo.product_qty or 0.0) - (mo.qty_produced or 0.0), 0.0)
        for move in mo.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel'))[:50]:
            self._from_move(move, result)
        if 'procurement_group_id' in mo._fields and mo.procurement_group_id and self.env.get('stock.move'):
            moves = self.env['stock.move'].search([
                ('group_id', '=', mo.procurement_group_id.id),
                ('state', 'not in', ('done', 'cancel')),
            ], limit=100)
            for move in moves:
                self._from_move(move, result)

    def _from_purchase(self, purchase, result):
        if not self._add_record_facts(purchase, result):
            return
        result['purchases'].add(purchase.id)
        self._add_impact_record('purchase', purchase, result, monetary_value=purchase.amount_total if 'amount_total' in purchase._fields else 0.0)
        result['path'].append(_('Purchase Order: %s') % purchase.display_name)
        if 'amount_total' in purchase._fields:
            result['purchase_value'] += purchase.amount_total or 0.0
        for line in purchase.order_line.filtered(lambda l: not l.display_type)[:50]:
            self._from_purchase_line(line, result)

    def _from_purchase_line(self, line, result):
        if not line.order_id:
            return
        if line.order_id.id not in result['purchases']:
            self._from_purchase(line.order_id, result)
            return
        if 'move_ids' in line._fields:
            for move in line.move_ids.filtered(lambda m: m.state not in ('done', 'cancel'))[:50]:
                self._from_move(move, result)

    def _from_account_move(self, move, result):
        self._add_record_facts(move, result)

    def _from_crm(self, lead, result):
        self._add_record_facts(lead, result)

    @staticmethod
    def _unique_path(path):
        seen = set()
        result = []
        for item in path:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result[:40]
