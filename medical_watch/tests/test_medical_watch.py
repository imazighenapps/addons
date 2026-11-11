# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMedVisit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "MedVisit Other Company"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "MedVisit Test Employee"})

    def _visit(self, **values):
        defaults = {
            "name": "VIS-2026-001",
            "employee_id": self.employee.id,
            "visit_type": "periodic",
            "scheduled_date": date(2026, 6, 10),
            "due_date": date(2026, 6, 30),
        }
        defaults.update(values)
        return self.env["medical.visit"].create(defaults)

    def test_01_visit_defaults(self):
        visit = self._visit(scheduled_date=date(2026, 12, 10),
                            due_date=date(2026, 12, 30))
        self.assertEqual(visit.state, "planned")
        self.assertEqual(visit.company_id, self.env.company)
        self.assertFalse(visit.is_overdue)

    def test_02_due_before_schedule_refused(self):
        with self.assertRaises(ValidationError):
            self._visit(name="VIS-2026-002", scheduled_date=date(2026, 7, 10),
                        due_date=date(2026, 7, 1))

    def test_03_done_requires_completion_date(self):
        visit = self._visit(name="VIS-2026-003")
        with self.assertRaises(ValidationError):
            visit.write({"state": "done", "done_date": False})

    def test_04_action_done_sets_state_and_date(self):
        visit = self._visit(name="VIS-2026-004")
        self.assertTrue(visit.action_done())
        self.assertEqual(visit.state, "done")
        self.assertTrue(visit.done_date)

    def test_05_cancel_and_reopen(self):
        visit = self._visit(name="VIS-2026-005")
        self.assertTrue(visit.action_cancel())
        self.assertEqual(visit.state, "cancelled")
        self.assertTrue(visit.action_reopen())
        self.assertEqual(visit.state, "planned")
        self.assertFalse(visit.done_date)

    def test_06_overdue_flag_computed(self):
        visit = self._visit(name="VIS-2026-006", scheduled_date=date(2026, 1, 1),
                            due_date=date(2026, 1, 31))
        visit.invalidate_recordset()
        self.assertTrue(visit.is_overdue)
        visit.action_done()
        visit.invalidate_recordset()
        self.assertFalse(visit.is_overdue)

    def test_07_cannot_complete_twice(self):
        visit = self._visit(name="VIS-2026-007")
        visit.action_done()
        with self.assertRaises(ValidationError):
            visit.action_done()

    def test_08_company_isolation(self):
        other_emp = self.env["hr.employee"].with_company(self.other_company).sudo().create({
            "name": "MedVisit Foreign Employee",
            "company_id": self.other_company.id,
        })
        foreign = self.env["medical.visit"].with_company(self.other_company).sudo().create({
            "name": "VIS-2026-OTH",
            "employee_id": other_emp.id,
            "visit_type": "initial",
            "scheduled_date": date(2026, 8, 1),
            "due_date": date(2026, 8, 15),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._visit(name="VIS-2026-LOC")
        self.assertNotEqual(local.company_id, foreign.company_id)
