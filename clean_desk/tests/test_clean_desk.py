# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHygieneBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "HygieneBook Other Company"})
        cls.user = cls.env.user

    def _plan(self, **values):
        defaults = {
            "name": "HygieneBook Test Daily Wash",
            "area": "Prep Room",
            "frequency": "daily",
            "method": "Detergent A",
            "responsible_id": self.user.id,
        }
        defaults.update(values)
        return self.env["cln.plan"].create(defaults)

    def _execution(self, plan, **values):
        defaults = {
            "name": "CLN-2026-001",
            "plan_id": plan.id,
            "scheduled_on": date(2026, 9, 10),
            "performer_id": self.user.id,
        }
        defaults.update(values)
        return self.env["cln.execution"].create(defaults)

    def test_01_defaults(self):
        plan = self._plan()
        exe = self._execution(plan)
        self.assertEqual(exe.state, "planned")
        self.assertEqual(plan.company_id, self.env.company)
        self.assertEqual(exe.area, "Prep Room")

    def test_02_done_workflow(self):
        plan = self._plan(name="HygieneBook Test Weekly")
        exe = self._execution(plan, name="CLN-2026-002")
        exe.performed_on = date(2026, 9, 10)
        self.assertTrue(exe.action_done())
        self.assertEqual(exe.state, "done")

    def test_03_done_requires_performed_date(self):
        plan = self._plan(name="HygieneBook Test Missing Date")
        exe = self._execution(plan, name="CLN-2026-003")
        with self.assertRaises(ValidationError):
            exe.action_done()

    def test_04_invalid_transitions(self):
        plan = self._plan(name="HygieneBook Test Transitions")
        exe = self._execution(plan, name="CLN-2026-004")
        exe.performed_on = date(2026, 9, 11)
        exe.action_done()
        with self.assertRaises(ValidationError):
            exe.action_cancel()
        with self.assertRaises(ValidationError):
            exe.action_reset()

    def test_05_date_constraint(self):
        plan = self._plan(name="HygieneBook Test Dates")
        with self.assertRaises(ValidationError):
            self._execution(plan, name="CLN-2026-005",
                            scheduled_on=date(2026, 9, 10),
                            performed_on=date(2026, 9, 9))

    def test_06_counters(self):
        plan = self._plan(name="HygieneBook Test Counters")
        e1 = self._execution(plan, name="CLN-2026-006A")
        e2 = self._execution(plan, name="CLN-2026-006B",
                             scheduled_on=date(2026, 9, 11))
        e1.performed_on = date(2026, 9, 10)
        e1.action_done()
        plan.invalidate_recordset()
        self.assertEqual(plan.execution_count, 2)
        self.assertEqual(plan.done_count, 1)
        self.assertEqual(plan.pending_count, 1)
        self.assertEqual(e2.state, "planned")

    def test_07_cancel_and_reset(self):
        plan = self._plan(name="HygieneBook Test Cancel")
        exe = self._execution(plan, name="CLN-2026-007")
        self.assertTrue(exe.action_cancel())
        self.assertEqual(exe.state, "cancelled")
        self.assertTrue(exe.action_reset())
        self.assertEqual(exe.state, "planned")

    def test_08_company_isolation(self):
        plan = self._plan(name="HygieneBook Test Local")
        foreign = self.env["cln.plan"].with_company(
            self.other_company).sudo().create({
            "name": "HygieneBook Foreign Plan",
            "area": "Foreign Area",
            "frequency": "weekly",
            "company_id": self.other_company.id,
        })
        self.assertEqual(plan.company_id, self.env.company)
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(plan.company_id, foreign.company_id)
