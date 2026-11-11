# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestUnitWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "UnitWatch Other Company"})

    def _check(self, **values):
        defaults = {
            "name": "UCHK-TEST-001",
            "document_ref": "PO/2026/001",
            "product_name": "Flour",
            "source": "order",
            "expected_unit": "kg",
            "entered_unit": "g",
            "quantity": 100.0,
            "checked_on": date(2026, 10, 5),
        }
        defaults.update(values)
        return self.env["unit.check"].create(defaults)

    def test_01_defaults(self):
        check = self._check()
        self.assertEqual(check.state, "open")
        self.assertTrue(check.is_suspicious)
        self.assertEqual(check.company_id, self.env.company)
        self.assertEqual(check.severity, "medium")

    def test_02_correct_flow(self):
        check = self._check(name="UCHK-CORR")
        check.corrected_qty = 0.1
        self.assertTrue(check.action_correct())
        self.assertEqual(check.state, "corrected")
        check.invalidate_recordset(["is_suspicious"])
        self.assertFalse(check.is_suspicious)

    def test_03_correct_requires_qty(self):
        check = self._check(name="UCHK-NOQTY")
        with self.assertRaises(UserError):
            check.action_correct()

    def test_04_dismiss_and_reopen(self):
        check = self._check(name="UCHK-DISMISS")
        self.assertTrue(check.action_dismiss())
        self.assertEqual(check.state, "dismissed")
        self.assertTrue(check.action_reopen())
        self.assertEqual(check.state, "open")
        with self.assertRaises(UserError):
            check.action_reopen()

    def test_05_same_units_refused(self):
        with self.assertRaises(ValidationError):
            self._check(name="UCHK-SAME", expected_unit="kg",
                        entered_unit="KG")

    def test_06_quantity_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._check(name="UCHK-QTY", quantity=0)

    def test_07_corrected_qty_required_when_corrected(self):
        with self.assertRaises(ValidationError):
            self.env["unit.check"].create({
                "name": "UCHK-BADCORR",
                "document_ref": "BILL/2026/01",
                "product_name": "Oil",
                "expected_unit": "L",
                "entered_unit": "cl",
                "quantity": 5.0,
                "corrected_qty": 0.0,
                "state": "corrected",
                "checked_on": date(2026, 10, 6),
            })

    def test_08_suspicious_filter(self):
        open_check = self._check(name="UCHK-OPEN")
        closed = self._check(name="UCHK-CLOSED", document_ref="PO/2026/002")
        closed.corrected_qty = 1.0
        closed.action_correct()
        found = self.env["unit.check"].search([("is_suspicious", "=", True)])
        self.assertIn(open_check, found)
        self.assertNotIn(closed, found)

    def test_09_company_isolation(self):
        foreign = self.env["unit.check"].with_company(
            self.other_company).create({
            "name": "UCHK-FOREIGN",
            "document_ref": "PO/F/001",
            "product_name": "Foreign",
            "expected_unit": "kg",
            "entered_unit": "lb",
            "quantity": 2.0,
            "checked_on": date(2026, 10, 7),
            "company_id": self.other_company.id,
        })
        local = self._check(name="UCHK-LOCAL")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(local.company_id, foreign.company_id)
