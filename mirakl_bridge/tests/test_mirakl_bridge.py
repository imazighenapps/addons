# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMiraklBridge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["mirakl.connection"].create({"name": "MK", "shop_id": "S1", "api_key_ref": "k"})
        cls.order = cls.env["mirakl.order"].create({"name": "MK-1", "connection_id": cls.conn.id, "amount_total": 50.0})

    def test_01_activate(self):
        c = self.env["mirakl.connection"].create({"name": "X", "shop_id": "S"})
        with self.assertRaises(UserError): c.action_activate()

    def test_02_accept_ship(self):
        self.order.action_accept()
        with self.assertRaises(UserError): self.order.action_ship()
        self.order.tracking_number = "TRK"; self.order.action_ship()
        self.assertEqual(self.order.state, "shipped")

    def test_03_full_flow(self):
        self.order.action_accept(); self.order.tracking_number = "T"; self.order.action_ship()
        self.order.action_invoice(); self.order.action_close()
        self.assertEqual(self.order.state, "closed")

    def test_04_closed_no_reset(self):
        self.order.action_accept(); self.order.tracking_number = "T"; self.order.action_ship()
        self.order.action_invoice(); self.order.action_close()
        with self.assertRaises(UserError): self.order.action_reset()

    def test_05_reset(self):
        self.order.action_accept(); self.order.action_reset(); self.assertEqual(self.order.state, "new")

    def test_06_amount_negative(self):
        with self.assertRaises(ValidationError):
            self.env["mirakl.order"].create({"name": "MK-B", "connection_id": self.conn.id, "amount_total": -1})

    def test_07_invoice_requires_ship(self):
        self.order.action_accept()
        with self.assertRaises(UserError): self.order.action_invoice()

    def test_08_close_requires_invoice(self):
        self.order.action_accept(); self.order.tracking_number = "T"; self.order.action_ship()
        with self.assertRaises(UserError): self.order.action_close()
