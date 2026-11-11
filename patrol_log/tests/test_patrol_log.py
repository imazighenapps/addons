# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPatrolBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "PatrolBook Other Company"})
        cls.start = datetime(2026, 3, 10, 22, 0, 0)

    def _round(self, **values):
        defaults = {
            "name": "PatrolBook Round A",
            "guard_name": "PatrolBook Guard A",
            "route": "PatrolBook Route North",
            "start_at": self.start,
            "company_id": self.env.company.id,
        }
        defaults.update(values)
        return self.env["patrol.round"].create(defaults)

    def _stop(self, round_rec, **values):
        defaults = {
            "name": "PatrolBook Gate A",
            "round_id": round_rec.id,
            "status": "visited",
            "checked_at": self.start + timedelta(minutes=10),
            "finding": False,
        }
        defaults.update(values)
        return self.env["patrol.stop"].create(defaults)

    def test_01_round_defaults(self):
        round_rec = self._round()
        self.assertEqual(round_rec.state, "draft")
        self.assertEqual(round_rec.company_id, self.env.company)
        self.assertEqual(round_rec.stop_count, 0)
        self.assertEqual(round_rec.skipped_count, 0)

    def test_02_complete_round(self):
        round_rec = self._round()
        self.assertTrue(round_rec.action_done())
        self.assertEqual(round_rec.state, "done")
        self.assertTrue(round_rec.end_at)

    def test_03_double_complete_is_refused(self):
        round_rec = self._round()
        round_rec.action_done()
        with self.assertRaises(ValidationError):
            round_rec.action_done()

    def test_04_round_end_before_start_is_refused(self):
        with self.assertRaises(ValidationError):
            self._round(end_at=self.start - timedelta(hours=1))

    def test_05_stop_before_round_start_is_refused(self):
        round_rec = self._round()
        with self.assertRaises(ValidationError):
            self._stop(round_rec, checked_at=self.start - timedelta(minutes=5))

    def test_06_skipped_stop_cannot_have_finding(self):
        round_rec = self._round()
        with self.assertRaises(ValidationError):
            self._stop(round_rec, name="PatrolBook Gate B",
                       status="skipped", finding=True)

    def test_07_round_counters(self):
        round_rec = self._round(name="PatrolBook Round B")
        self._stop(round_rec, name="PatrolBook Stop 1")
        self._stop(round_rec, name="PatrolBook Stop 2",
                   checked_at=self.start + timedelta(minutes=20),
                   status="skipped")
        self._stop(round_rec, name="PatrolBook Stop 3",
                   checked_at=self.start + timedelta(minutes=30),
                   finding=True)
        round_rec.invalidate_recordset()
        self.assertEqual(round_rec.stop_count, 3)
        self.assertEqual(round_rec.skipped_count, 1)
        self.assertEqual(round_rec.finding_count, 1)

    def test_08_finding_filter(self):
        round_rec = self._round(name="PatrolBook Round C")
        issue = self._stop(round_rec, name="PatrolBook Stop F",
                           finding=True)
        self._stop(round_rec, name="PatrolBook Stop N",
                   checked_at=self.start + timedelta(minutes=15))
        found = self.env["patrol.stop"].search([
            ("finding", "=", True), ("round_id", "=", round_rec.id)])
        self.assertIn(issue, found)
        self.assertEqual(len(found), 1)

    def test_09_company_isolation(self):
        foreign = self.env["patrol.round"].with_company(
            self.other_company).create({
            "name": "PatrolBook Foreign Round",
            "guard_name": "PatrolBook Guard Z",
            "route": "PatrolBook Route South",
            "start_at": self.start,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._round(name="PatrolBook Local Round")
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
