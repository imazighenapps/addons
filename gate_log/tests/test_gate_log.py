# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGateBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "GateBook Other Company",
        })
        cls.carrier = cls.env["res.partner"].create({
            "name": "GateBook Test Carrier",
        })
        cls.gate = cls.env["gate.point"].create({
            "name": "GateBook Test North Gate",
            "code": "GB-N",
            "location": "North Yard",
        })
        cls.gate_s = cls.env["gate.point"].create({
            "name": "GateBook Test South Gate",
            "code": "GB-S",
        })

    def _entry(self, gate=None, **values):
        defaults = {
            "name": "GateBook Test Visit",
            "gate_id": (gate or self.gate).id,
            "truck_plate": "GB-TEST-001",
            "carrier_id": self.carrier.id,
            "driver_name": "GateBook Test Driver",
            "purpose": "delivery",
            "entered_at": datetime(2026, 11, 10, 8, 0, 0),
        }
        defaults.update(values)
        return self.env["gate.entry"].create(defaults)

    def test_01_entry_defaults(self):
        entry = self._entry()
        self.assertEqual(entry.state, "on_site")
        self.assertEqual(entry.company_id, self.env.company)
        self.assertEqual(entry.wait_minutes, 0.0)
        self.assertFalse(entry.exited_at)

    def test_02_close_sets_exit_and_wait(self):
        entry = self._entry()
        self.assertTrue(entry.action_close())
        self.assertEqual(entry.state, "closed")
        self.assertTrue(entry.exited_at)
        self.assertGreaterEqual(entry.wait_minutes, 0.0)

    def test_03_double_close_is_refused(self):
        entry = self._entry()
        entry.action_close()
        with self.assertRaises(UserError):
            entry.action_close()

    def test_04_reopen_clears_exit(self):
        entry = self._entry()
        entry.action_close()
        self.assertTrue(entry.action_reopen())
        self.assertEqual(entry.state, "on_site")
        self.assertFalse(entry.exited_at)
        self.assertEqual(entry.wait_minutes, 0.0)
        with self.assertRaises(UserError):
            entry.action_reopen()

    def test_05_exit_before_entry_is_refused(self):
        with self.assertRaises(ValidationError):
            self._entry(entered_at=datetime(2026, 11, 10, 10, 0, 0),
                        exited_at=datetime(2026, 11, 10, 9, 0, 0))

    def test_06_wait_minutes_computed(self):
        entry = self._entry(entered_at=datetime(2026, 11, 10, 8, 0, 0))
        entry.write({
            "state": "closed",
            "exited_at": datetime(2026, 11, 10, 9, 30, 0),
        })
        self.assertAlmostEqual(entry.wait_minutes, 90.0, places=2)
        entry.write({"exited_at": datetime(2026, 11, 10, 10, 0, 0)})
        self.assertAlmostEqual(entry.wait_minutes, 120.0, places=2)

    def test_07_gate_counters(self):
        on_site = self._entry(name="GateBook Test Open")
        closed = self._entry(name="GateBook Test Closed",
                             truck_plate="GB-TEST-002")
        closed.action_close()
        self.gate.invalidate_recordset()
        self.assertEqual(self.gate.entry_count, 2)
        self.assertEqual(self.gate.open_entry_count, 1)
        self.assertEqual(on_site.state, "on_site")

    def test_08_company_isolation(self):
        foreign_gate = self.env["gate.point"].with_company(
            self.other_company).sudo().create({
            "name": "GateBook Test Foreign Gate",
            "company_id": self.other_company.id,
        })
        foreign = self.env["gate.entry"].with_company(
            self.other_company).sudo().create({
            "name": "GateBook Test Foreign Entry",
            "gate_id": foreign_gate.id,
            "truck_plate": "GB-FOREIGN-1",
            "entered_at": datetime(2026, 12, 1, 7, 0, 0),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._entry(name="GateBook Test Local")
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)

    def test_09_filters_by_state(self):
        on_site = self._entry(name="GateBook Test Filter Open")
        closed = self._entry(name="GateBook Test Filter Closed",
                             truck_plate="GB-TEST-003")
        closed.action_close()
        found = self.env["gate.entry"].search([
            ("state", "=", "on_site"),
            ("gate_id", "=", self.gate.id),
        ])
        self.assertIn(on_site, found)
        self.assertNotIn(closed, found)
