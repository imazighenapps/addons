# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAllegroBridge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["allegro.connection"].create({"name": "A", "account_login": "shop"})
        cls.offer = cls.env["allegro.offer"].create({"name": "Offer", "connection_id": cls.conn.id, "price": 5.0})
        cls.order = cls.env["allegro.order"].create({"name": "A-1", "connection_id": cls.conn.id, "amount_total": 15.0})

    def test_01_activate(self):
        c = self.env["allegro.connection"].create({"name": "X"})
        with self.assertRaises(UserError): c.action_activate()

    def test_02_offer_negative(self):
        with self.assertRaises(ValidationError): self.offer.write({"stock_qty": -1})

    def test_03_offer_states(self):
        self.offer.action_activate(); self.assertEqual(self.offer.state, "active")
        self.offer.action_end(); self.assertEqual(self.offer.state, "ended")

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
            self.env["allegro.order"].create({"name": "A-B", "connection_id": self.conn.id, "amount_total": -1})
