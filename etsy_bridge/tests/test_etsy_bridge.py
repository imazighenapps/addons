# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEtsyBridge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["etsy.connection"].create({"name": "Shop", "shop_name": "MyShop"})
        cls.listing = cls.env["etsy.listing"].create({"name": "L1", "connection_id": cls.conn.id, "price": 10.0, "stock_qty": 5})
        cls.order = cls.env["etsy.order"].create({"name": "E-1", "connection_id": cls.conn.id, "amount_total": 20.0})

    def test_01_activate(self):
        c = self.env["etsy.connection"].create({"name": "X"})
        with self.assertRaises(UserError): c.action_activate()

    def test_02_listing_vals(self):
        with self.assertRaises(ValidationError): self.listing.write({"price": -1})

    def test_03_listing_states(self):
        self.listing.action_activate(); self.assertEqual(self.listing.state, "active")
        self.listing.action_deactivate(); self.assertEqual(self.listing.state, "inactive")

    def test_04_order_flow(self):
        self.order.action_process(); self.order.action_ship(); self.assertEqual(self.order.state, "shipped")

    def test_05_shipped_no_cancel(self):
        self.order.action_process(); self.order.action_ship()
        with self.assertRaises(UserError): self.order.action_cancel()

    def test_06_cancel(self):
        self.order.action_cancel(); self.assertEqual(self.order.state, "canceled")

    def test_07_reset(self):
        self.order.action_process(); self.order.action_reset(); self.assertEqual(self.order.state, "new")

    def test_08_amount_negative(self):
        with self.assertRaises(ValidationError):
            self.env["etsy.order"].create({"name": "E-B", "connection_id": self.conn.id, "amount_total": -1})
