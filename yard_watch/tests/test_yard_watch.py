# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestYardWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "YardWatch Other Company"})
        cls.slot = cls.env["yard.slot"].create({
            "name": "YW-SLOT-A1",
            "dock": "Dock 1",
            "capacity": 2,
        })
        cls.slot_b = cls.env["yard.slot"].create({
            "name": "YW-SLOT-B1",
            "dock": "Dock 2",
            "capacity": 1,
        })

    def _trailer(self, slot=None, **values):
        defaults = {
            "name": "YW-TR-%s" % self.env["ir.sequence"].next_by_code("seq") if False else "YW-TR-TEST",
            "carrier": "YardWatch Carrier",
            "slot_id": (slot or self.slot).id,
            "arrived_on": datetime(2026, 5, 10, 8, 0, 0),
        }
        defaults.update(values)
        if "name" not in values:
            defaults["name"] = "YW-TR-%s" % (self.env["yard.trailer"].search_count([]) + 1)
        return self.env["yard.trailer"].create(defaults)

    def test_01_trailer_defaults(self):
        trailer = self._trailer(name="YW-TR-DEFAULT")
        self.assertEqual(trailer.state, "waiting")
        self.assertEqual(trailer.company_id, self.env.company)
        self.assertFalse(trailer.docked_on)
        self.assertFalse(trailer.departed_on)
        self.assertGreaterEqual(trailer.wait_hours, 0.0)

    def test_02_dock_and_depart_workflow(self):
        trailer = self._trailer(name="YW-TR-FLOW")
        self.assertTrue(trailer.action_dock())
        self.assertEqual(trailer.state, "docked")
        self.assertTrue(trailer.docked_on)
        self.assertTrue(trailer.action_depart())
        self.assertEqual(trailer.state, "departed")
        self.assertTrue(trailer.departed_on)

    def test_03_dock_only_waiting(self):
        trailer = self._trailer(name="YW-TR-DOCK")
        trailer.action_dock()
        with self.assertRaises(ValidationError):
            trailer.action_dock()

    def test_04_double_depart_is_refused(self):
        trailer = self._trailer(name="YW-TR-DEP")
        trailer.action_depart()
        with self.assertRaises(ValidationError):
            trailer.action_depart()

    def test_05_departure_before_arrival_is_refused(self):
        with self.assertRaises(ValidationError):
            self._trailer(
                name="YW-TR-BADDATE",
                arrived_on=datetime(2026, 5, 10, 10, 0, 0),
                departed_on=datetime(2026, 5, 10, 9, 0, 0),
            )

    def test_06_wait_hours_computed(self):
        trailer = self._trailer(
            name="YW-TR-HOURS",
            arrived_on=datetime(2026, 5, 10, 8, 0, 0),
            departed_on=datetime(2026, 5, 10, 11, 30, 0),
        )
        self.assertAlmostEqual(trailer.wait_hours, 3.5, places=2)

    def test_07_slot_counts(self):
        t1 = self._trailer(name="YW-TR-C1", slot=self.slot)
        t2 = self._trailer(name="YW-TR-C2", slot=self.slot)
        t2.action_dock()
        self.slot.invalidate_recordset()
        self.assertEqual(self.slot.waiting_count, 1)
        self.assertEqual(self.slot.docked_count, 1)
        t1.action_depart()
        self.slot.invalidate_recordset()
        self.assertEqual(self.slot.waiting_count, 0)

    def test_08_company_isolation(self):
        foreign_slot = self.env["yard.slot"].with_company(
            self.other_company).sudo().create({
            "name": "YW-FOREIGN-SLOT",
            "dock": "Dock X",
            "capacity": 1,
            "company_id": self.other_company.id,
        })
        foreign = self.env["yard.trailer"].with_company(
            self.other_company).sudo().create({
            "name": "YW-FOREIGN-TR",
            "carrier": "Foreign Carrier",
            "slot_id": foreign_slot.id,
            "arrived_on": datetime(2026, 5, 10, 8, 0, 0),
            "company_id": self.other_company.id,
        })
        local = self._trailer(name="YW-LOCAL-TR", slot=self.slot_b)
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
