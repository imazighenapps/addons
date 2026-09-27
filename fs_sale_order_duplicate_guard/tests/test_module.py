from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from psycopg2 import IntegrityError


class TestDuplicateGuard(TransactionCase):

    def test_normalize(self):
        service = self.env['fs.sale.order.duplicate.mixin']
        self.assertEqual(service._normalize(' a-b / 12 '), 'AB12')

    def test_configuration_tolerances(self):
        config = self.env['fs.sale.order.duplicate.config'].create({'company_id': self.env.company.id})
        self.assertTrue(config.compare_reference)
        self.assertTrue(config.compare_lines)
        self.assertEqual(config.amount_tolerance, 0.0)

    def test_invalid_tolerance_is_rejected(self):
        with self.assertRaises(IntegrityError):
            self.env['fs.sale.order.duplicate.config'].create({
                'company_id': self.env.company.id,
                'quantity_tolerance': -1,
            })

    def test_same_customer_reference_increases_score(self):
        partner = self.env['res.partner'].create({'name': 'Duplicate Customer'})
        product = self.env['product.product'].create({'name': 'Duplicate Product', 'list_price': 10.0})
        order_1 = self.env['sale.order'].create({'partner_id': partner.id, 'client_order_ref': 'REF-001'})
        order_2 = self.env['sale.order'].create({'partner_id': partner.id, 'client_order_ref': 'REF-001'})
        for order in (order_1, order_2):
            self.env['sale.order.line'].create({
                'order_id': order.id,
                'product_id': product.id,
                'product_uom_qty': 2.0,
                'product_uom_id': product.uom_id.id,
                'price_unit': 10.0,
            })
        config = self.env['fs.sale.order.duplicate.config'].create({'company_id': self.env.company.id})
        score, factors = self.env['fs.sale.order.duplicate.mixin']._score_orders(order_2, order_1, config)
        self.assertGreaterEqual(score, 70)
        self.assertIn('Same customer reference', factors)
