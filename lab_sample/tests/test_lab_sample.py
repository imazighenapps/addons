# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLabWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "LabWatch Other Company"})

    def _sample(self, **values):
        defaults = {
            "name": "LAB 2026-11-09-A",
            "lot_ref": "LOT-2026-001",
            "barcode": "BC-001",
            "laboratory": "LabWatch External Lab",
            "sent_on": date(2026, 11, 9),
        }
        defaults.update(values)
        return self.env["lab.sample"].create(defaults)

    def test_01_sample_defaults(self):
        record = self._sample(name="LAB 2026-11-09-DEF")
        self.assertEqual(record.state, "sent")
        self.assertEqual(record.outcome, "pending")
        self.assertEqual(record.company_id, self.env.company)
        self.assertFalse(record.received_on)

    def test_02_receive_requires_outcome(self):
        record = self._sample(name="LAB 2026-11-10-A")
        with self.assertRaises(UserError):
            record.action_receive()

    def test_03_receive_with_pass_outcome(self):
        record = self._sample(name="LAB 2026-11-10-B", outcome="pass")
        self.assertTrue(record.action_receive())
        self.assertEqual(record.state, "received")
        self.assertTrue(record.received_on)
        self.assertEqual(record.outcome, "pass")

    def test_04_receive_with_fail_outcome(self):
        record = self._sample(name="LAB 2026-11-10-C", outcome="fail")
        self.assertTrue(record.action_receive())
        self.assertEqual(record.state, "received")
        self.assertEqual(record.outcome, "fail")

    def test_05_double_receive_is_refused(self):
        record = self._sample(name="LAB 2026-11-11-A", outcome="pass")
        record.action_receive()
        with self.assertRaises(UserError):
            record.action_receive()

    def test_06_received_before_sent_is_refused(self):
        with self.assertRaises(ValidationError):
            self._sample(
                name="LAB 2026-11-11-B",
                sent_on=date(2026, 11, 9),
                received_on=date(2026, 11, 2))

    def test_07_pending_outcome_cannot_be_received_state(self):
        with self.assertRaises(ValidationError):
            self._sample(
                name="LAB 2026-11-11-C",
                state="received",
                outcome="pending",
                received_on=date(2026, 11, 10))

    def test_08_awaiting_search_finds_sent_only(self):
        awaiting = self._sample(name="LAB 2026-11-12-A")
        done = self._sample(name="LAB 2026-11-12-B", outcome="pass")
        done.action_receive()
        found = self.env["lab.sample"].search([
            ("state", "=", "sent"),
            ("name", "in", [awaiting.name, done.name])])
        self.assertIn(awaiting, found)
        self.assertNotIn(done, found)

    def test_09_company_isolation(self):
        foreign = self.env["lab.sample"].with_company(
            self.other_company).sudo().create({
            "name": "LAB 2026-11-12-FOREIGN",
            "lot_ref": "LOT-F-001",
            "barcode": "BC-F-001",
            "laboratory": "Foreign Lab",
            "sent_on": date(2026, 11, 12),
            "company_id": self.other_company.id,
        })
        local = self._sample(name="LAB 2026-11-12-C")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
