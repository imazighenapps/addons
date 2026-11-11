# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAuditBinder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "AuditBinder Other Company"})
        cls.binder = cls.env["audit.binder"].create({
            "name": "AuditBinder 2026-Q1",
            "period_start": date(2026, 1, 1),
            "period_end": date(2026, 3, 31),
        })

    def _item(self, binder=None, **values):
        defaults = {
            "binder_id": (binder or self.binder).id,
            "section_name": "Bank",
            "name": "Bank statement",
            "reference": "BNK/2026/01",
        }
        defaults.update(values)
        return self.env["audit.binder.item"].create(defaults)

    def test_01_binder_defaults(self):
        self.assertEqual(self.binder.state, "draft")
        self.assertEqual(self.binder.company_id, self.env.company)
        self.assertFalse(self.binder.closed_on)

    def test_02_collect_and_close_workflow(self):
        item = self._item()
        self.assertTrue(self.binder.action_start_collecting())
        self.assertEqual(self.binder.state, "collecting")
        self.assertTrue(item.action_mark_ready())
        self.assertTrue(self.binder.action_close())
        self.assertEqual(self.binder.state, "closed")
        self.assertTrue(self.binder.closed_on)

    def test_03_close_with_missing_item_is_refused(self):
        self._item(name="Missing bank statement")
        self.binder.action_start_collecting()
        with self.assertRaises(ValidationError):
            self.binder.action_close()

    def test_04_ready_without_reference_is_refused(self):
        item = self._item(name="No ref item", reference=False)
        with self.assertRaises(ValidationError):
            item.action_mark_ready()

    def test_05_period_end_before_start_is_refused(self):
        with self.assertRaises(ValidationError):
            self.env["audit.binder"].create({
                "name": "AuditBinder Bad Period",
                "period_start": date(2026, 9, 30),
                "period_end": date(2026, 9, 1),
            })

    def test_06_progress_counters(self):
        ready = self._item(name="Ready item", reference="REF-001")
        ready.action_mark_ready()
        missing = self._item(name="Missing item", reference="REF-002",
                             section_name="VAT")
        self.binder.invalidate_recordset()
        self.assertEqual(self.binder.item_count, 2)
        self.assertEqual(self.binder.missing_item_count, 1)
        self.assertTrue(missing)

    def test_07_start_collecting_needs_items(self):
        binder = self.env["audit.binder"].create({
            "name": "AuditBinder Empty",
            "period_start": date(2026, 10, 1),
            "period_end": date(2026, 10, 31),
        })
        with self.assertRaises(ValidationError):
            binder.action_start_collecting()

    def test_08_company_isolation(self):
        foreign = self.env["audit.binder"].with_company(
            self.other_company).sudo().create({
            "name": "AuditBinder Foreign",
            "period_start": date(2026, 11, 1),
            "period_end": date(2026, 11, 30),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self.env["audit.binder"].create({
            "name": "AuditBinder Local",
            "period_start": date(2026, 12, 1),
            "period_end": date(2026, 12, 31),
        })
        self.assertEqual(local.company_id, self.env.company)
