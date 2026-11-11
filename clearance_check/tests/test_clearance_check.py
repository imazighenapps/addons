# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestClearance(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "Clearance Other Company"})
        cls.user = cls.env.user

    def _check(self, **values):
        defaults = {
            "name": "CLR-2026-001",
            "line_area": "Line A",
            "outgoing_product": "Product Old",
            "incoming_product": "Product New",
            "planned_on": datetime(2026, 7, 10, 8, 0, 0),
            "responsible_id": self.user.id,
        }
        defaults.update(values)
        return self.env["clc.check"].create(defaults)

    def _item(self, check, **values):
        defaults = {
            "check_id": check.id,
            "name": "Clearance Test Remove labels",
            "item_type": "remove",
        }
        defaults.update(values)
        return self.env["clc.item"].create(defaults)

    def test_01_defaults(self):
        rec = self._check()
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.company_id, self.env.company)
        self.assertEqual(rec.item_count, 0)

    def test_02_full_workflow(self):
        rec = self._check(name="CLR-2026-002")
        item = self._item(rec)
        self.assertTrue(rec.action_start())
        self.assertTrue(item.action_done())
        self.assertEqual(item.state, "done")
        rec.invalidate_recordset()
        self.assertTrue(rec.action_mark_ready())
        self.assertTrue(rec.action_release())
        self.assertEqual(rec.state, "released")
        self.assertTrue(rec.released_on)

    def test_03_ready_requires_items(self):
        rec = self._check(name="CLR-2026-003")
        rec.action_start()
        with self.assertRaises(ValidationError):
            rec.action_mark_ready()
        self._item(rec)
        with self.assertRaises(ValidationError):
            rec.action_mark_ready()

    def test_04_invalid_transitions(self):
        rec = self._check(name="CLR-2026-004")
        with self.assertRaises(ValidationError):
            rec.action_release()
        with self.assertRaises(ValidationError):
            rec.action_mark_ready()

    def test_05_item_signoff(self):
        rec = self._check(name="CLR-2026-005")
        item = self._item(rec, name="Clearance Test Verify tools")
        item.action_done()
        self.assertEqual(item.signed_by_id, self.user)
        self.assertTrue(item.signed_on)
        with self.assertRaises(ValidationError):
            item.action_done()

    def test_06_counters(self):
        rec = self._check(name="CLR-2026-006")
        i1 = self._item(rec, name="Clearance Test Clean surface")
        i2 = self._item(rec, name="Clearance Test Remove parts")
        i1.action_done()
        rec.invalidate_recordset()
        self.assertEqual(rec.item_count, 2)
        self.assertEqual(rec.done_item_count, 1)
        self.assertEqual(i2.state, "todo")

    def test_07_released_items_locked(self):
        rec = self._check(name="CLR-2026-007")
        item = self._item(rec, name="Clearance Test Verify bin")
        rec.action_start()
        item.action_done()
        rec.invalidate_recordset()
        rec.action_mark_ready()
        rec.action_release()
        with self.assertRaises(ValidationError):
            item.action_reset()

    def test_08_company_isolation(self):
        rec = self._check(name="CLR-2026-008")
        foreign = self.env["clc.check"].with_company(
            self.other_company).sudo().create({
            "name": "CLR-FOREIGN-2026",
            "line_area": "Line Z",
            "planned_on": datetime(2026, 8, 1, 7, 0, 0),
            "company_id": self.other_company.id,
        })
        self.assertEqual(rec.company_id, self.env.company)
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(rec.company_id, foreign.company_id)
