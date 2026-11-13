# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMondialRelayShip(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["mondialrelay.connection"].create({
            "name": "MR", "merchant_id": "M123",
        })
        cls.point = cls.env["mondialrelay.point"].create({
            "name": "Relay A", "relay_code": "FR-001", "city": "Paris",
        })
        cls.partner = cls.env["res.partner"].create({"name": "Client"})
        cls.ship = cls.env["mondialrelay.shipment"].create({
            "name": "MR-TEST-1", "connection_id": cls.conn.id,
            "partner_id": cls.partner.id, "relay_point_id": cls.point.id,
            "weight": 2.0,
        })

    def test_01_activate_requires_merchant(self):
        c = self.env["mondialrelay.connection"].create({"name": "No"})
        with self.assertRaises(UserError):
            c.action_activate()

    def test_02_prepare_requires_relay(self):
        s = self.env["mondialrelay.shipment"].create({
            "name": "MR-TEST-2", "connection_id": self.conn.id, "weight": 1.0,
        })
        with self.assertRaises(UserError):
            s.action_prepare()

    def test_03_full_flow(self):
        self.ship.action_prepare()
        self.assertEqual(self.ship.state, "ready")
        self.ship.action_label()
        self.assertEqual(self.ship.state, "label")
        self.assertTrue(self.ship.tracking_number)
        self.ship.action_ship()
        self.assertEqual(self.ship.state, "in_transit")
        self.ship.action_deliver()
        self.assertEqual(self.ship.state, "delivered")

    def test_04_delivered_cannot_reset(self):
        self.ship.action_prepare(); self.ship.action_label()
        self.ship.action_ship(); self.ship.action_deliver()
        with self.assertRaises(UserError):
            self.ship.action_reset()

    def test_05_reset_clears_tracking(self):
        self.ship.action_prepare(); self.ship.action_label()
        self.ship.action_reset()
        self.assertEqual(self.ship.state, "draft")
        self.assertFalse(self.ship.tracking_number)

    def test_06_weight_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.env["mondialrelay.shipment"].create({
                "name": "MR-BAD", "connection_id": self.conn.id, "weight": 0.0,
            })

    def test_07_events_logged(self):
        self.ship.action_prepare(); self.ship.action_label()
        self.assertTrue(self.ship.event_ids)

    def test_08_relay_code_unique(self):
        with self.assertRaises(Exception):
            self.env["mondialrelay.point"].create({"name": "Dup", "relay_code": "FR-001"})
