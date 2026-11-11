# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestContainerWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ContainerWatch Other Company"})
        cls.currency = cls.env.company.currency_id

    def _shipment(self, **values):
        defaults = {
            "name": "CW-TEST-001",
            "booking_ref": "BK-001",
            "vessel": "Ever Test",
            "origin": "Shanghai",
            "destination": "Rotterdam",
            "eta": date(2026, 12, 15),
            "currency_id": self.currency.id,
        }
        defaults.update(values)
        return self.env["container.shipment"].create(defaults)

    def _charge(self, shipment, amount=100.0, **values):
        defaults = {
            "shipment_id": shipment.id,
            "name": "Freight",
            "charge_type": "freight",
            "payer": "us",
            "amount": amount,
        }
        defaults.update(values)
        return self.env["container.charge"].create(defaults)

    def test_01_defaults(self):
        ship = self._shipment()
        self.assertEqual(ship.state, "booked")
        self.assertEqual(ship.company_id, self.env.company)
        self.assertEqual(ship.total_amount, 0.0)
        self.assertFalse(ship.is_delayed)

    def test_02_flow_booked_to_released(self):
        ship = self._shipment(name="CW-FLOW")
        ship.action_sail()
        self.assertEqual(ship.state, "at_sea")
        ship.action_mark_arrived()
        self.assertEqual(ship.state, "arrived")
        ship.action_release()
        self.assertEqual(ship.state, "released")
        self.assertTrue(ship.arrived_on)

    def test_03_invalid_transitions(self):
        ship = self._shipment(name="CW-INV")
        with self.assertRaises(UserError):
            ship.action_mark_arrived()
        ship.action_sail()
        with self.assertRaises(UserError):
            ship.action_sail()

    def test_04_charges_totals_and_due(self):
        ship = self._shipment(name="CW-CHG")
        self._charge(ship, 500.0, name="Freight 1")
        self._charge(ship, 200.0, name="Demurrage", charge_type="demurrage",
                     settled=True)
        ship.invalidate_recordset(["total_amount", "due_amount", "charge_count"])
        self.assertEqual(ship.charge_count, 2)
        self.assertAlmostEqual(ship.total_amount, 700.0)
        self.assertAlmostEqual(ship.due_amount, 500.0)

    def test_05_negative_charge_refused(self):
        ship = self._shipment(name="CW-NEG")
        with self.assertRaises(ValidationError):
            self._charge(ship, -10.0, name="Bad")

    def test_06_released_locks_charges(self):
        ship = self._shipment(name="CW-LOCK")
        charge = self._charge(ship, 100.0)
        ship.action_sail()
        ship.action_mark_arrived()
        ship.action_release()
        with self.assertRaises(UserError):
            self._charge(ship, 50.0, name="Late")
        with self.assertRaises(UserError):
            charge.write({"amount": 120.0})

    def test_07_delay_flag(self):
        ship = self._shipment(name="CW-DELAY", eta=date(2026, 1, 1))
        ship.invalidate_recordset(["is_delayed"])
        self.assertTrue(ship.is_delayed)
        ship.action_sail()
        ship.invalidate_recordset(["is_delayed"])
        self.assertTrue(ship.is_delayed)

    def test_08_company_isolation(self):
        foreign = self.env["container.shipment"].with_company(
            self.other_company).create({
            "name": "CW-FOREIGN",
            "origin": "Busan",
            "destination": "Hamburg",
            "currency_id": self.env.company.currency_id.id,
            "company_id": self.other_company.id,
        })
        local = self._shipment(name="CW-LOCAL")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(local.company_id, foreign.company_id)
