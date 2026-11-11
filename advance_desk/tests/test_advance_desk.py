# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPayAdvance(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "PayAdvance Other Company"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "PayAdvance Test Employee"})
        cls.other_employee = cls.env["hr.employee"].create({
            "name": "PayAdvance Other Employee"})

    def _request(self, **values):
        defaults = {
            "name": "ADV-2026-001",
            "employee_id": self.employee.id,
            "amount": 1200.0,
            "request_date": date(2026, 1, 10),
        }
        defaults.update(values)
        return self.env["advance.request"].create(defaults)

    def _line(self, request, **values):
        defaults = {
            "request_id": request.id,
            "due_date": date(2026, 2, 1),
            "amount": 300.0,
        }
        defaults.update(values)
        return self.env["advance.repayment"].create(defaults)

    def test_01_request_defaults(self):
        req = self._request(name="ADV-2026-DEF")
        self.assertEqual(req.state, "draft")
        self.assertEqual(req.company_id, self.env.company)
        self.assertEqual(req.remaining_amount, 1200.0)

    def test_02_submit_and_approve(self):
        req = self._request()
        self.assertTrue(req.action_submit())
        self.assertEqual(req.state, "submitted")
        self.assertTrue(req.action_approve())
        self.assertEqual(req.state, "approved")
        self.assertTrue(req.approval_date)

    def test_03_amount_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._request(amount=0)

    def test_04_schedule_cannot_exceed_amount(self):
        req = self._request(amount=500.0)
        self._line(req, amount=300.0, due_date=date(2026, 2, 1))
        with self.assertRaises(ValidationError):
            self._line(req, amount=250.0, due_date=date(2026, 3, 1))

    def test_05_repayment_updates_balance(self):
        req = self._request(amount=600.0)
        line1 = self._line(req, amount=200.0, due_date=date(2026, 2, 1))
        line2 = self._line(req, amount=400.0, due_date=date(2026, 3, 1))
        self.assertEqual(req.remaining_amount, 600.0)
        line1.action_mark_paid()
        req.invalidate_recordset()
        self.assertEqual(req.repaid_amount, 200.0)
        self.assertEqual(req.remaining_amount, 400.0)
        self.assertEqual(line2.state, "planned")

    def test_06_close_requires_full_repayment(self):
        req = self._request(amount=400.0)
        line = self._line(req, amount=400.0, due_date=date(2026, 4, 1))
        req.action_submit()
        req.action_approve()
        with self.assertRaises(ValidationError):
            req.action_close()
        line.action_mark_paid()
        req.invalidate_recordset()
        self.assertTrue(req.action_close())
        self.assertEqual(req.state, "repaid")

    def test_07_refuse_from_submitted(self):
        req = self._request()
        req.action_submit()
        self.assertTrue(req.action_refuse())
        self.assertEqual(req.state, "refused")
        with self.assertRaises(ValidationError):
            req.action_approve()

    def test_08_company_isolation(self):
        other_emp = self.env["hr.employee"].with_company(self.other_company).sudo().create({
            "name": "PayAdvance Foreign Employee",
            "company_id": self.other_company.id,
        })
        foreign = self.env["advance.request"].with_company(self.other_company).sudo().create({
            "name": "ADV-2026-OTH",
            "employee_id": other_emp.id,
            "amount": 800.0,
            "request_date": date(2026, 1, 15),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._request(name="ADV-2026-LOC")
        self.assertNotEqual(foreign.company_id, local.company_id)
