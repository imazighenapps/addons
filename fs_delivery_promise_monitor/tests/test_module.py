from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestDeliveryPromiseMonitor(TransactionCase):

    def test_configuration_defaults(self):
        config = self.env['fs.delivery.promise.monitor.config'].create({'company_id': self.env.company.id})
        self.assertGreater(config.warning_hours, 0)
        self.assertEqual(config.notification_mode, 'activity')

    def test_refresh_empty_is_safe(self):
        self.env['fs.delivery.promise.risk'].refresh(self.env['sale.order'])

    def test_future_promise_is_safe(self):
        partner = self.env['res.partner'].create({'name': 'Delivery Promise Test Customer'})
        order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'commitment_date': fields.Datetime.now() + timedelta(days=10),
        })
        result = self.env['fs.delivery.promise.risk']._evaluate_order(order)
        self.assertEqual(result['status'], 'safe')
        self.assertTrue(result['open'])

    def test_past_promise_with_open_delivery_is_late(self):
        partner = self.env['res.partner'].create({'name': 'Late Promise Test Customer'})
        order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'commitment_date': fields.Datetime.now() - timedelta(days=2),
        })
        result = self.env['fs.delivery.promise.risk']._evaluate_order(order)
        self.assertEqual(result['status'], 'late')
        self.assertTrue(result['open'])
