from odoo.tests.common import TransactionCase


class TestVendorAck(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env['res.partner'].create({
            'name': 'Vendor Ack Test Supplier',
            'supplier_rank': 1,
            'email': 'supplier@example.com',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Vendor Ack Test Product',
        })
        cls.purchase = cls.env['purchase.order'].create({'partner_id': cls.vendor.id})
        cls.env['purchase.order.line'].create({
            'order_id': cls.purchase.id,
            'product_id': cls.product.id,
            'product_qty': 5.0,
            'product_uom_id': cls.product.uom_id.id,
            'price_unit': 10.0,
        })

    def test_token_is_unique_and_valid_state_is_restricted(self):
        ack = self.env['fs.purchase.vendor.ack'].create_from_purchase_order(self.purchase)
        self.assertTrue(ack.access_token)
        self.assertTrue(ack._is_token_valid())
        ack.with_context(fs_vendor_ack_transition=True).write({'state': 'superseded'})
        self.assertFalse(ack._is_token_valid())

    def test_purchase_line_change_creates_new_acknowledgment_version(self):
        ack = self.env['fs.purchase.vendor.ack'].create_from_purchase_order(self.purchase)
        ack.with_context(fs_vendor_ack_transition=True).write({'state': 'submitted'})
        line = self.purchase.order_line[:1]
        line.write({'product_qty': 7.0})
        acks = self.env['fs.purchase.vendor.ack'].search(
            [('purchase_order_id', '=', self.purchase.id)], order='version'
        )
        self.assertEqual(acks[-2].state, 'superseded')
        self.assertEqual(acks[-1].state, 'draft')
        self.assertGreater(acks[-1].version, ack.version)
        self.assertEqual(acks[-1].line_ids.ordered_qty, 7.0)
