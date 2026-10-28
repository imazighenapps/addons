# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPriceGuard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "PriceGuard Test Supplier", "supplier_rank": 1})
        cls.product = cls.env["product.product"].create({
            "name": "PriceGuard Test Product", "type": "service",
            "standard_price": 100.0, "list_price": 100.0})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"),
             ("company_id", "=", cls.env.company.id)], limit=1)
        if not cls.journal:
            cls.journal = cls.env["account.journal"].create({
                "name": "PriceGuard Purchases", "code": "PGPUR",
                "type": "purchase"})
        cls.expense = cls.env["account.account"].search(
            [("account_type", "=", "expense"),
             ("company_ids", "in", cls.env.company.id)], limit=1)
        cls.agreement = cls.env["price.agreement"].create({
            "name": "PriceGuard Framework 2026",
            "partner_id": cls.partner.id,
            "product_id": cls.product.id,
            "price": 100.0,
            "min_qty": 1.0,
            "date_from": date(2026, 1, 1),
            "date_to": date(2026, 12, 31),
            "tolerance_percent": 2.0,
        })
        cls.agreement.action_activate()

    def _bill(self, amount, bill_date=None, post=True, product=None):
        bill_date = bill_date or date(2026, 6, 1)
        line = {
            "product_id": (product or self.product).id,
            "name": "PriceGuard service",
            "quantity": 1.0,
            "price_unit": amount,
            "tax_ids": [(5, 0, 0)],
        }
        if self.expense:
            line["account_id"] = self.expense.id
        bill = self.env["account.move"].create({
            "move_type": "in_invoice",
            "partner_id": self.partner.id,
            "journal_id": self.journal.id,
            "invoice_date": bill_date,
            "invoice_line_ids": [(0, 0, line)],
        })
        if post:
            bill.action_post()
        return bill

    def _check(self, bill):
        return self.env["price.check"].search([
            ("invoice_id", "=", bill.id)], limit=1)

    def test_01_scan_at_agreed_price(self):
        bill = self._bill(100.0, post=False)
        self.assertEqual(self.env["price.scanner"].action_scan(self.agreement.ids), 0)
        bill.action_post()
        self.assertEqual(self.env["price.scanner"].action_scan(self.agreement.ids), 1)
        check = self._check(bill)
        self.assertTrue(check.name.startswith("PC/"))
        self.assertEqual(check.status, "ok")
        self.assertAlmostEqual(check.invoice_price, 100.0, places=2)
        self.assertAlmostEqual(check.agreed_price, 100.0, places=2)
        self.assertAlmostEqual(check.difference_percent, 0.0, places=2)

    def test_02_small_increase_is_ok(self):
        bill = self._bill(101.0)
        self.env["price.scanner"].action_scan(self.agreement.ids)
        check = self._check(bill)
        self.assertEqual(check.status, "ok")
        self.assertAlmostEqual(check.difference_percent, 1.0, places=2)

    def test_03_above_tolerance_is_warning(self):
        bill = self._bill(103.0)
        self.env["price.scanner"].action_scan(self.agreement.ids)
        check = self._check(bill)
        self.assertEqual(check.status, "warning")
        self.assertAlmostEqual(check.difference_percent, 3.0, places=2)

    def test_04_large_increase_is_breach(self):
        bill = self._bill(110.0)
        self.env["price.scanner"].action_scan(self.agreement.ids)
        check = self._check(bill)
        self.assertEqual(check.status, "breach")
        self.assertAlmostEqual(check.difference_percent, 10.0, places=2)

    def test_05_expired_agreement_not_matched(self):
        product = self.env["product.product"].create({
            "name": "PriceGuard Expired Product", "type": "service",
            "standard_price": 50.0, "list_price": 50.0})
        agreement = self.env["price.agreement"].create({
            "name": "PriceGuard Expired Agreement",
            "partner_id": self.partner.id,
            "product_id": product.id,
            "price": 50.0,
            "date_from": date(2026, 1, 1),
            "date_to": date(2026, 12, 31),
        })
        agreement.action_activate()
        agreement.action_expire()
        bill = self._bill(80.0, product=product)
        self.assertEqual(self.env["price.scanner"].action_scan(self.agreement.ids), 0)
        self.assertFalse(self._check(bill))

    def test_06_scan_is_idempotent(self):
        bill = self._bill(110.0)
        self.assertEqual(self.env["price.scanner"].action_scan(self.agreement.ids), 1)
        self.assertEqual(self.env["price.scanner"].action_scan(self.agreement.ids), 0)
        self.assertEqual(self.env["price.check"].search_count([
            ("invoice_id", "=", bill.id)]), 1)

    def test_07_ignore_and_reset(self):
        bill = self._bill(110.0)
        self.env["price.scanner"].action_scan(self.agreement.ids)
        check = self._check(bill)
        self.assertEqual(check.status, "breach")
        check.action_ignore()
        self.assertEqual(check.status, "ignored")
        check.action_reset()
        self.assertEqual(check.status, "breach")

    def test_08_agreement_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["price.agreement"].create({
                "name": "PriceGuard Invalid Price",
                "partner_id": self.partner.id,
                "product_id": self.product.id,
                "price": 0.0,
            })
        with self.assertRaises(ValidationError):
            self.env["price.agreement"].create({
                "name": "PriceGuard Invalid Dates",
                "partner_id": self.partner.id,
                "product_id": self.product.id,
                "price": 10.0,
                "date_from": date(2026, 5, 10),
                "date_to": date(2026, 5, 1),
            })
        with self.assertRaises(ValidationError):
            self.env["price.agreement"].create({
                "name": "PriceGuard Invalid Tolerance",
                "partner_id": self.partner.id,
                "product_id": self.product.id,
                "price": 10.0,
                "tolerance_percent": -1.0,
            })
