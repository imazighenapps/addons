# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProbation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "Probation Other Company"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "Probation Test Employee"})

    def _period(self, **values):
        defaults = {
            "name": "PROB-2026-001",
            "employee_id": self.employee.id,
            "start_date": date(2026, 1, 10),
            "end_date": date(2026, 4, 10),
            "review_date": date(2026, 4, 1),
        }
        defaults.update(values)
        return self.env["probation.period"].create(defaults)

    def test_01_defaults(self):
        period = self._period()
        self.assertEqual(period.state, "ongoing")
        self.assertEqual(period.company_id, self.env.company)
        self.assertFalse(period.decision)

    def test_02_dates_constraints(self):
        with self.assertRaises(ValidationError):
            self._period(name="PROB-2026-002", start_date=date(2026, 5, 1),
                         end_date=date(2026, 4, 1), review_date=date(2026, 4, 20))
        with self.assertRaises(ValidationError):
            self._period(name="PROB-2026-003", start_date=date(2026, 5, 10),
                         end_date=date(2026, 6, 10), review_date=date(2026, 5, 1))

    def test_03_confirm_sets_decision(self):
        period = self._period(name="PROB-2026-004")
        self.assertTrue(period.action_confirm())
        self.assertEqual(period.state, "decided")
        self.assertEqual(period.decision, "confirm")
        self.assertTrue(period.decision_date)

    def test_04_extend_and_close(self):
        period = self._period(name="PROB-2026-005")
        self.assertTrue(period.action_extend())
        self.assertEqual(period.decision, "extend")
        period.action_reopen()
        self.assertTrue(period.action_close())
        self.assertEqual(period.decision, "close")

    def test_05_reopen_clears_decision(self):
        period = self._period(name="PROB-2026-006")
        period.action_confirm()
        self.assertTrue(period.action_reopen())
        self.assertEqual(period.state, "ongoing")
        self.assertFalse(period.decision)
        self.assertFalse(period.decision_date)

    def test_06_overdue_flag(self):
        period = self._period(name="PROB-2026-007", start_date=date(2026, 1, 1),
                              end_date=date(2026, 2, 1), review_date=date(2026, 1, 20))
        period.invalidate_recordset()
        self.assertTrue(period.is_overdue)
        period.action_confirm()
        period.invalidate_recordset()
        self.assertFalse(period.is_overdue)

    def test_07_decided_cannot_decide_again(self):
        period = self._period(name="PROB-2026-008")
        period.action_confirm()
        with self.assertRaises(ValidationError):
            period.action_close()

    def test_08_company_isolation(self):
        other_emp = self.env["hr.employee"].with_company(self.other_company).sudo().create({
            "name": "Probation Foreign Employee",
            "company_id": self.other_company.id,
        })
        foreign = self.env["probation.period"].with_company(self.other_company).sudo().create({
            "name": "PROB-2026-OTH",
            "employee_id": other_emp.id,
            "start_date": date(2026, 3, 1),
            "end_date": date(2026, 6, 1),
            "review_date": date(2026, 5, 20),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._period(name="PROB-2026-LOC")
        self.assertNotEqual(local.company_id, foreign.company_id)
