# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOvertimeDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "OverTime Other Company"})
        cls.department = cls.env["hr.department"].create({
            "name": "OverTime Operations"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "OverTime Test Employee",
            "department_id": cls.department.id,
        })

    def _request(self, **values):
        defaults = {
            "name": "OverTime Request 2026-01",
            "employee_id": self.employee.id,
            "request_date": "2026-05-10",
            "hours_requested": 2.5,
            "reason": "Month-end closing support.",
        }
        defaults.update(values)
        return self.env["overtime.request"].create(defaults)

    def test_01_request_defaults(self):
        req = self._request()
        self.assertEqual(req.state, "draft")
        self.assertEqual(req.company_id, self.env.company)
        self.assertEqual(req.hours_approved, 0.0)
        self.assertEqual(req.department_id, self.department)

    def test_02_approve_sets_approved_hours(self):
        req = self._request(name="OverTime Request 2026-02")
        self.assertTrue(req.action_approve())
        self.assertEqual(req.state, "approved")
        self.assertAlmostEqual(req.hours_approved, req.hours_requested)

    def test_03_reject_keeps_zero_approved_hours(self):
        req = self._request(name="OverTime Request 2026-03")
        self.assertTrue(req.action_reject())
        self.assertEqual(req.state, "rejected")
        self.assertEqual(req.hours_approved, 0.0)

    def test_04_reset_to_draft(self):
        req = self._request(name="OverTime Request 2026-04")
        req.action_reject()
        self.assertTrue(req.action_reset_draft())
        self.assertEqual(req.state, "draft")
        self.assertEqual(req.hours_approved, 0.0)

    def test_05_double_approve_is_refused(self):
        req = self._request(name="OverTime Request 2026-05")
        req.action_approve()
        with self.assertRaises(ValidationError):
            req.action_approve()

    def test_06_reject_non_draft_is_refused(self):
        req = self._request(name="OverTime Request 2026-06")
        req.action_approve()
        with self.assertRaises(ValidationError):
            req.action_reject()

    def test_07_hours_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._request(name="OverTime Request 2026-07", hours_requested=0)
        with self.assertRaises(ValidationError):
            self._request(name="OverTime Request 2026-08", hours_requested=-1.5)

    def test_08_reset_draft_on_draft_is_refused(self):
        req = self._request(name="OverTime Request 2026-09")
        with self.assertRaises(ValidationError):
            req.action_reset_draft()

    def test_09_approved_hours_recompute_on_reset(self):
        req = self._request(name="OverTime Request 2026-10", hours_requested=3.0)
        req.action_approve()
        self.assertAlmostEqual(req.hours_approved, 3.0)
        req.action_reset_draft()
        self.assertEqual(req.hours_approved, 0.0)

    def test_10_company_isolation(self):
        foreign_department = self.env["hr.department"].with_company(
            self.other_company).create({
            "name": "OverTime Foreign Dept",
            "company_id": self.other_company.id,
        })
        foreign_employee = self.env["hr.employee"].with_company(
            self.other_company).create({
            "name": "OverTime Foreign Employee",
            "company_id": self.other_company.id,
            "department_id": foreign_department.id,
        })
        foreign = self.env["overtime.request"].with_company(
            self.other_company).create({
            "name": "OverTime Foreign Request",
            "employee_id": foreign_employee.id,
            "request_date": "2026-06-12",
            "hours_requested": 1.0,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._request(name="OverTime Local Request 2026-11")
        self.assertNotEqual(foreign.company_id, local.company_id)
