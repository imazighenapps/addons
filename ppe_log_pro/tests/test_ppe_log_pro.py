# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGuardKit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "GuardKit Other Company"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "GuardKit Test Employee"})
        cls.item = cls.env["ppe.item"].create({
            "name": "GuardKit Test Gloves",
            "code": "GL-1",
            "category": "hand",
            "standard": "EN 388",
            "validity_months": 6,
        })
        cls.helmet = cls.env["ppe.item"].create({
            "name": "GuardKit Test Helmet",
            "category": "head",
            "validity_months": 12,
        })

    def _issue(self, item=None, **values):
        defaults = {
            "item_id": (item or self.item).id,
            "employee_id": self.employee.id,
            "size": "L",
            "quantity": 1,
            "issued_on": date(2026, 11, 9),
        }
        defaults.update(values)
        return self.env["ppe.issue"].create(defaults)

    def test_01_issue_defaults(self):
        issue = self._issue()
        self.assertEqual(issue.state, "issued")
        self.assertEqual(issue.company_id, self.env.company)
        self.assertTrue(issue.name.startswith("PPE "))
        self.assertTrue(issue.expires_on)
        self.assertFalse(issue.signed)

    def test_02_renewal_date_comes_from_the_item(self):
        issue = self._issue(issued_on=date(2026, 11, 9))
        self.assertEqual(issue.expires_on, date(2027, 5, 9))
        other = self._issue(item=self.helmet,
                            issued_on=date(2026, 11, 9))
        self.assertEqual(other.expires_on, date(2027, 11, 9))

    def test_03_return_stamps_the_date(self):
        issue = self._issue()
        self.assertTrue(issue.action_return())
        self.assertEqual(issue.state, "returned")
        self.assertTrue(issue.returned_on)

    def test_04_double_return_is_refused(self):
        issue = self._issue()
        issue.action_return()
        with self.assertRaises(UserError):
            issue.action_return()

    def test_05_quantity_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._issue(quantity=0)
        with self.assertRaises(ValidationError):
            self._issue(quantity=-2)

    def test_06_return_before_issue_is_refused(self):
        with self.assertRaises(ValidationError):
            self._issue(issued_on=date(2026, 11, 9),
                        returned_on=date(2026, 11, 2))

    def test_07_item_counters(self):
        open_issue = self._issue()
        closed = self._issue(size="M")
        closed.action_return()
        self.item.invalidate_recordset()
        self.assertEqual(self.item.issue_count, 2)
        self.assertEqual(self.item.open_issue_count, 1)
        self.assertTrue(open_issue)

    def test_08_signed_flag_and_filter(self):
        issue = self._issue(signed=True)
        found = self.env["ppe.issue"].search([
            ("signed", "=", True), ("state", "=", "issued")])
        self.assertIn(issue, found)
        signed_second = self._issue()
        self.assertFalse(signed_second.signed)

    def test_09_company_isolation(self):
        foreign_employee = self.env["hr.employee"].sudo().create({
            "name": "GuardKit Test Foreign Employee"})
        foreign = self.env["ppe.issue"].with_company(
            self.other_company).sudo().create({
            "item_id": self.item.id,
            "employee_id": foreign_employee.id,
            "issued_on": date(2026, 11, 9),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._issue()
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
