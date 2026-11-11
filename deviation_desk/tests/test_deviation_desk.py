# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDeviation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "Deviation Other Company"})
        cls.user = cls.env.user

    def _deviation(self, **values):
        defaults = {
            "name": "DEVD-2026-001",
            "product_ref": "Batch A-2026",
            "area": "Filling Line 1",
            "detected_on": date(2026, 3, 10),
            "owner_id": self.user.id,
        }
        defaults.update(values)
        return self.env["devd.deviation"].create(defaults)

    def _impact(self, deviation, **values):
        defaults = {
            "deviation_id": deviation.id,
            "reviewed_on": date(2026, 3, 11),
            "reviewer_id": self.user.id,
            "risk_level": "medium",
            "judgement": "Deviation Test Impact Judgement",
        }
        defaults.update(values)
        return self.env["devd.impact"].create(defaults)

    def _approval(self, deviation, **values):
        defaults = {
            "deviation_id": deviation.id,
            "approver_id": self.user.id,
            "decided_on": date(2026, 3, 12),
            "decision": "granted",
        }
        defaults.update(values)
        return self.env["devd.approval"].create(defaults)

    def test_01_defaults(self):
        rec = self._deviation()
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.company_id, self.env.company)
        self.assertEqual(rec.detected_on, date(2026, 3, 10))

    def test_02_workflow_to_close(self):
        rec = self._deviation(name="DEVD-2026-002")
        self.assertTrue(rec.action_investigate())
        self._approval(rec)
        rec.invalidate_recordset()
        self.assertTrue(rec.action_mark_approved())
        self.assertTrue(rec.action_close())
        self.assertEqual(rec.state, "closed")
        self.assertTrue(rec.closed_on)

    def test_03_close_requires_approval(self):
        rec = self._deviation(name="DEVD-2026-003")
        rec.action_investigate()
        with self.assertRaises(ValidationError):
            rec.action_mark_approved()

    def test_04_invalid_state_transitions(self):
        rec = self._deviation(name="DEVD-2026-004")
        with self.assertRaises(ValidationError):
            rec.action_close()
        rec.action_investigate()
        with self.assertRaises(ValidationError):
            rec.action_investigate()

    def test_05_date_constraints(self):
        rec = self._deviation(name="DEVD-2026-005")
        with self.assertRaises(ValidationError):
            self._impact(rec, reviewed_on=date(2026, 3, 1))
        with self.assertRaises(ValidationError):
            self._approval(rec, decided_on=date(2026, 3, 1))

    def test_06_counters(self):
        rec = self._deviation(name="DEVD-2026-006")
        self._impact(rec)
        self._impact(rec, reviewed_on=date(2026, 3, 13))
        self._approval(rec, decision="granted")
        self._approval(rec, decision="rejected", decided_on=date(2026, 3, 14))
        rec.invalidate_recordset()
        self.assertEqual(rec.impact_count, 2)
        self.assertEqual(rec.approval_count, 2)
        self.assertEqual(rec.granted_approval_count, 1)

    def test_07_closed_cannot_reopen(self):
        rec = self._deviation(name="DEVD-2026-007")
        rec.action_investigate()
        self._approval(rec)
        rec.invalidate_recordset()
        rec.action_mark_approved()
        rec.action_close()
        with self.assertRaises(ValidationError):
            rec.action_reset()

    def test_08_company_isolation(self):
        rec = self._deviation(name="DEVD-2026-008")
        foreign = self.env["devd.deviation"].with_company(
            self.other_company).sudo().create({
            "name": "DEVD-FOREIGN-2026",
            "product_ref": "Batch F",
            "area": "Remote",
            "detected_on": date(2026, 4, 1),
            "company_id": self.other_company.id,
        })
        self.assertEqual(rec.company_id, self.env.company)
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(rec.company_id, foreign.company_id)
