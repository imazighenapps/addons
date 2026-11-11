# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVendorReturn(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "VendorReturn Other Company"})
        cls.currency = cls.env.company.currency_id

    def _return(self, **values):
        defaults = {
            "name": "RVD-2026-001",
            "vendor_name": "VendorReturn Supplier A",
            "reference": "CLM-2026-01",
            "transport_ref": "TRK-2026-100",
            "return_date": date(2026, 3, 10),
            "expected_credit": 250.0,
            "currency_id": self.currency.id,
        }
        defaults.update(values)
        return self.env["rvd.return"].create(defaults)

    def _line(self, ret, **values):
        defaults = {
            "return_id": ret.id,
            "product_name": "VendorReturn Widget",
            "quantity": 2.0,
            "reason": "Damaged on receipt",
        }
        defaults.update(values)
        return self.env["rvd.return.line"].create(defaults)

    def test_01_return_defaults(self):
        rec = self._return()
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.company_id, self.env.company)
        self.assertFalse(rec.credit_received)
        self.assertFalse(rec.credit_pending)
        self.assertEqual(rec.line_count, 0)

    def test_02_send_and_credit_workflow(self):
        rec = self._return()
        self.assertTrue(rec.action_send())
        self.assertEqual(rec.state, "sent")
        self.assertTrue(rec.credit_pending)
        self.assertTrue(rec.action_mark_credited())
        self.assertEqual(rec.state, "credited")
        self.assertTrue(rec.credit_received)
        self.assertFalse(rec.credit_pending)

    def test_03_close_from_credited(self):
        rec = self._return()
        rec.action_send()
        rec.action_mark_credited()
        self.assertTrue(rec.action_close())
        self.assertEqual(rec.state, "closed")

    def test_04_invalid_transitions_refused(self):
        rec = self._return()
        with self.assertRaises(ValidationError):
            rec.action_mark_credited()
        rec.action_send()
        rec.action_mark_credited()
        with self.assertRaises(ValidationError):
            rec.action_send()

    def test_05_expected_credit_must_be_non_negative(self):
        with self.assertRaises(ValidationError):
            self._return(expected_credit=-10.0)

    def test_06_received_credit_requires_positive_amount(self):
        with self.assertRaises(ValidationError):
            self._return(expected_credit=0.0, credit_received=True)

    def test_07_line_quantity_must_be_positive(self):
        rec = self._return()
        with self.assertRaises(ValidationError):
            self._line(rec, quantity=0.0)
        with self.assertRaises(ValidationError):
            self._line(rec, quantity=-1.0)

    def test_08_line_count_stored(self):
        rec = self._return()
        self._line(rec, product_name="VendorReturn Part A")
        self._line(rec, product_name="VendorReturn Part B", quantity=3.0)
        rec.invalidate_recordset()
        self.assertEqual(rec.line_count, 2)

    def test_09_credit_pending_filter_logic(self):
        rec = self._return(name="RVD-2026-002")
        rec.action_send()
        self.assertTrue(rec.credit_pending)
        found = self.env["rvd.return"].search([
            ("credit_pending", "=", True)])
        self.assertIn(rec, found)
        rec.action_mark_credited()
        self.assertFalse(rec.credit_pending)

    def test_10_company_isolation(self):
        foreign = self.env["rvd.return"].with_company(
            self.other_company).sudo().create({
            "name": "RVD-2026-F1",
            "vendor_name": "VendorReturn Foreign Supplier",
            "return_date": date(2026, 4, 5),
            "expected_credit": 100.0,
            "currency_id": self.other_company.currency_id.id,
            "company_id": self.other_company.id,
        })
        local = self._return(name="RVD-2026-L1")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
