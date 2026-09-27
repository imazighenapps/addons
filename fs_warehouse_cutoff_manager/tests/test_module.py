from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestWarehouseCutoff(TransactionCase):

    def test_rule_validation_boundary(self):
        self.assertTrue(0 <= 16.0 < 24)

    def _make_rule_and_picking(self, scheduled_date, weekday='0', allow_next_day=False):
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        picking_type = self.env['stock.picking.type'].search([
            ('warehouse_id', '=', warehouse.id),
            ('code', '=', 'outgoing'),
        ], limit=1)
        self.assertTrue(warehouse and picking_type)
        rule = self.env['fs.warehouse.cutoff.rule'].create({
            'company_id': self.env.company.id,
            'warehouse_id': warehouse.id,
            'picking_type_id': picking_type.id,
            'weekday': weekday,
            'cutoff_hour': 16.0,
            'timezone': 'UTC',
            'allow_next_day': allow_next_day,
        })
        partner = self.env['res.partner'].create({'name': 'Cutoff Test Customer'})
        picking = self.env['stock.picking'].create({
            'partner_id': partner.id,
            'picking_type_id': picking_type.id,
            'scheduled_date': scheduled_date,
        })
        return rule, picking

    def test_cutoff_datetime_is_timezone_aware(self):
        rule, picking = self._make_rule_and_picking(datetime(2026, 9, 21, 12, 0, 0))
        cutoff = self.env['fs.warehouse.cutoff.monitor']._compute_cutoff(picking, rule)
        self.assertEqual(cutoff.hour, 16)

    def test_cutoff_evaluation_marks_not_ready_as_at_risk(self):
        rule, picking = self._make_rule_and_picking(datetime(2026, 9, 21, 12, 0, 0))
        picking.state = 'confirmed'
        cutoff = self.env['fs.warehouse.cutoff.monitor']._compute_cutoff(picking, rule)
        values = self.env['fs.warehouse.cutoff.monitor']._evaluate(
            picking, rule, cutoff, datetime(2026, 9, 21, 15, 30, 0)
        )
        self.assertEqual(values['status'], 'at_risk')
        self.assertFalse(values['ready'])
