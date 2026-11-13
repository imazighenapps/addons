# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDpdShip(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["dpd.connection"].create({"name": "DPD", "customer_number": "CN1"})
        cls.ship = cls.env["dpd.shipment"].create({"name": "D1", "connection_id": cls.conn.id, "weight": 1.0})

    def test_01_activate(self):
        c = self.env["dpd.connection"].create({"name": "X"})
        with self.assertRaises(UserError): c.action_activate()

    def test_02_flow(self):
        self.ship.action_prepare(); self.ship.action_label(); self.ship.action_ship(); self.ship.action_deliver()
        self.assertEqual(self.ship.state, "delivered")

    def test_03_reset(self):
        self.ship.action_prepare(); self.ship.action_label(); self.ship.action_reset()
        self.assertEqual(self.ship.state, "draft")

    def test_04_delivered_no_reset(self):
        self.ship.action_prepare(); self.ship.action_label(); self.ship.action_ship(); self.ship.action_deliver()
        with self.assertRaises(UserError): self.ship.action_reset()

    def test_05_weight_positive(self):
        with self.assertRaises(ValidationError):
            self.env["dpd.shipment"].create({"name": "B", "connection_id": self.conn.id, "weight": 0})

    def test_06_label_required(self):
        self.ship.action_prepare()
        with self.assertRaises(UserError): self.ship.action_ship()

    def test_07_events(self):
        self.ship.action_prepare(); self.assertTrue(self.ship.event_ids)

    def test_08_tracking_set(self):
        self.ship.action_prepare(); self.ship.action_label()
        self.assertTrue(self.ship.tracking_number)
