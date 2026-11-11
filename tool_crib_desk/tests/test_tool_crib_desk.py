# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestToolCrib(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ToolCrib Other Company"})
        cls.tool = cls.env["tool.crib.tool"].create({
            "name": "ToolCrib Torque Wrench",
            "code": "TW-01",
            "condition": "good",
        })

    def _loan(self, **values):
        defaults = {
            "tool_id": self.tool.id,
            "borrower_name": "ToolCrib Borrower A",
            "issued_on": date(2026, 5, 4),
            "due_on": date(2026, 5, 11),
            "company_id": self.env.company.id,
        }
        defaults.update(values)
        return self.env["tool.crib.loan"].create(defaults)

    def test_01_loan_defaults(self):
        loan = self._loan()
        self.assertEqual(loan.state, "out")
        self.assertEqual(loan.company_id, self.env.company)
        self.assertTrue(loan.name.startswith("Loan "))

    def test_02_return_stamps_date(self):
        loan = self._loan()
        self.assertTrue(loan.action_return())
        self.assertEqual(loan.state, "returned")
        self.assertTrue(loan.returned_on)

    def test_03_double_return_is_refused(self):
        loan = self._loan()
        loan.action_return()
        with self.assertRaises(ValidationError):
            loan.action_return()

    def test_04_due_before_issue_is_refused(self):
        with self.assertRaises(ValidationError):
            self._loan(issued_on=date(2026, 5, 4),
                       due_on=date(2026, 5, 1))

    def test_05_return_before_issue_is_refused(self):
        with self.assertRaises(ValidationError):
            self._loan(issued_on=date(2026, 5, 4),
                       returned_on=date(2026, 5, 2))

    def test_06_late_flag(self):
        loan = self._loan(issued_on=date(2026, 1, 5),
                          due_on=date(2026, 1, 12))
        loan.invalidate_recordset()
        self.assertTrue(loan.is_late)

    def test_07_tool_counters(self):
        open_loan = self._loan(borrower_name="ToolCrib Borrower B")
        closed = self._loan(borrower_name="ToolCrib Borrower C",
                            issued_on=date(2026, 5, 5),
                            due_on=date(2026, 5, 12))
        closed.action_return()
        self.tool.invalidate_recordset()
        self.assertEqual(self.tool.loan_count, 2)
        self.assertEqual(self.tool.open_loan_count, 1)
        self.assertEqual(open_loan.state, "out")

    def test_08_open_loans_filter(self):
        out = self._loan(borrower_name="ToolCrib Borrower D")
        closed = self._loan(borrower_name="ToolCrib Borrower E",
                            issued_on=date(2026, 5, 6),
                            due_on=date(2026, 5, 13))
        closed.action_return()
        found = self.env["tool.crib.loan"].search([
            ("state", "=", "out"), ("tool_id", "=", self.tool.id)])
        self.assertIn(out, found)
        self.assertNotIn(closed, found)

    def test_09_condition_field(self):
        other = self.env["tool.crib.tool"].create({
            "name": "ToolCrib Drill",
            "code": "DR-01",
            "condition": "worn",
        })
        self.assertEqual(other.condition, "worn")
        good = self.env["tool.crib.tool"].search([
            ("condition", "=", "good"), ("id", "=", self.tool.id)])
        self.assertIn(self.tool, good)

    def test_10_company_isolation(self):
        foreign_tool = self.env["tool.crib.tool"].with_company(
            self.other_company).create({
            "name": "ToolCrib Foreign Tool",
            "company_id": self.other_company.id,
        })
        foreign = self.env["tool.crib.loan"].with_company(
            self.other_company).create({
            "tool_id": foreign_tool.id,
            "borrower_name": "ToolCrib Borrower Z",
            "issued_on": date(2026, 5, 4),
            "due_on": date(2026, 5, 11),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._loan(borrower_name="ToolCrib Borrower L")
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
