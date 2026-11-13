# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestColissimoShip(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["colissimo.connection"].create({"name": "Coli", "contract_number": "C123"})
        cls.partner = cls.env["res.partner"].create({"name": "Cust"})
        cls.ship = cls.env["colissimo.shipment"].create({
            "name": "COL-T1", "connection_id": cls.conn.id, "partner_id": cls.partner.id, "weight": 1.0,
        })

    def test_01_activate(self):
        c = self.env["colissimo.connection"].create({"name": "X"})
        with self.assertRaises(UserError):
            c.action_activate()
        c.contract_number = "A"; c.action_activate(); self.assertEqual(c.state, "active")

    def test_02_prepare_requires_partner(self):
        s = self.env["colissimo.shipment"].create({"name": "C2", "connection_id": self.conn.id})
        with self.assertRaises(UserError): s.action_prepare()

    def test_03_flow(self):
        self.ship.action_prepare(); self.ship.action_label(); self.ship.action_ship(); self.ship.action_deliver()
        self.assertEqual(self.ship.state, "delivered")
        self.assertTrue(self.ship.tracking_number)

    def test_04_delivered_no_reset(self):
        self.ship.action_prepare(); self.ship.action_label(); self.ship.action_ship(); self.ship.action_deliver()
        with self.assertRaises(UserError): self.ship.action_reset()

    def test_05_reset_clears(self):
        self.ship.action_prepare(); self.ship.action_label(); self.ship.action_reset()
        self.assertFalse(self.ship.tracking_number)

    def test_06_weight_positive(self):
        with self.assertRaises(ValidationError):
            self.env["colissimo.shipment"].create({"name": "BAD", "connection_id": self.conn.id, "weight": -1})

    def test_07_events(self):
        self.ship.action_prepare(); self.assertTrue(self.ship.event_ids)

    def test_08_ship_requires_label(self):
        self.ship.action_prepare()
        with self.assertRaises(UserError): self.ship.action_ship()
