from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCustomerOrderSnapshot(TransactionCase):

    def test_configuration_defaults(self):
        config = self.env['fs.customer.order.snapshot.config'].create({'company_id': self.env.company.id})
        self.assertEqual(config.max_orders, 5)
        self.assertEqual(config.lookback_days, 365)
        self.assertTrue(config.include_prices)
        self.assertTrue(config.include_discounts)

    def test_invalid_max_orders_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env['fs.customer.order.snapshot.config'].create({
                'company_id': self.env.company.id,
                'max_orders': 0,
            })

    def test_invalid_lookback_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env['fs.customer.order.snapshot.config'].create({
                'company_id': self.env.company.id,
                'lookback_days': 0,
            })

    def test_wizard_model_exists(self):
        self.assertIn('fs.customer.order.snapshot.wizard', self.env)
