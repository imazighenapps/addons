# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDepositPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The French e-invoicing pack blocks the posting of customer invoices
        # that do not carry the full legal mentions. Test invoices are
        # technical fixtures, so the block is lifted for the duration of the
        # class (the transaction is rolled back afterwards).
        params = cls.env["ir.config_parameter"].sudo()
        block = params.search(
            [("key", "=", "fr_einvoicing_pack.block_noncompliant")], limit=1)
        if block:
            block.write({"value": "False"})
        else:
            params.create({
                "key": "fr_einvoicing_pack.block_noncompliant",
                "value": "False"})
        cls.partner = cls.env["res.partner"].create({
            "name": "DepositPro Test Customer", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "DepositPro Test Service", "type": "service",
            "list_price": 500.0, "taxes_id": [(5, 0, 0)]})
        cls.journal = cls.env["account.journal"].search([
            ("type", "=", "sale"),
            ("company_id", "=", cls.env.company.id)], limit=1)
        cls.income = cls.env["account.account"].search([
            ("account_type", "=", "income"),
            ("company_ids", "in", cls.env.company.id)], limit=1)
        cls.invoice = cls._make_invoice(cls.partner, 500.0)

    @classmethod
    def _make_invoice(cls, partner, amount=500.0):
        invoice = cls.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": partner.id,
            "journal_id": cls.journal.id,
            "invoice_date": date(2026, 1, 15),
            "invoice_line_ids": [(0, 0, {
                "product_id": cls.product.id,
                "name": "Consulting service",
                "quantity": 1,
                "price_unit": amount,
                "account_id": cls.income.id,
                "tax_ids": [(5, 0, 0)],
            })],
        })
        invoice.action_post()
        return invoice

    def _deposit(self, amount=500.0, confirm=True, partner=None):
        deposit = self.env["customer.deposit"].create({
            "partner_id": (partner or self.partner).id,
            "amount": amount,
            "reference": "TEST-DEP",
        })
        if confirm:
            deposit.action_confirm()
        return deposit

    def _allocate(self, deposit, invoice=None, amount=100.0):
        return self.env["deposit.allocation"].create({
            "deposit_id": deposit.id,
            "invoice_id": (invoice or self.invoice).id,
            "amount": amount,
        })

    def test_01_confirm(self):
        deposit = self._deposit(confirm=False)
        self.assertTrue(deposit.name.startswith("DEP/"))
        self.assertEqual(deposit.state, "draft")
        deposit.action_confirm()
        self.assertEqual(deposit.state, "confirmed")
        with self.assertRaises(UserError):
            deposit.action_confirm()

    def test_02_remaining_amount(self):
        deposit = self._deposit(500.0)
        self.assertAlmostEqual(deposit.allocated_amount, 0.0, places=2)
        self.assertAlmostEqual(deposit.remaining_amount, 500.0, places=2)
        self.assertEqual(deposit.allocation_count, 0)

    def test_03_partial_allocation(self):
        deposit = self._deposit(500.0, confirm=False)
        with self.assertRaises(UserError):
            self._allocate(deposit, amount=100.0)
        deposit.action_confirm()
        self._allocate(deposit, amount=200.0)
        self.assertEqual(deposit.state, "partial")
        self.assertAlmostEqual(deposit.allocated_amount, 200.0, places=2)
        self.assertAlmostEqual(deposit.remaining_amount, 300.0, places=2)
        self.assertEqual(deposit.allocation_count, 1)

    def test_04_full_allocation(self):
        deposit = self._deposit(500.0)
        self._allocate(deposit, amount=500.0)
        self.assertEqual(deposit.state, "applied")
        self.assertAlmostEqual(deposit.remaining_amount, 0.0, places=2)

    def test_05_over_allocation(self):
        deposit = self._deposit(500.0)
        with self.assertRaises(ValidationError):
            self._allocate(deposit, amount=600.0)
        second = self._deposit(500.0)
        self._allocate(second, amount=300.0)
        self.assertAlmostEqual(second.remaining_amount, 200.0, places=2)
        with self.assertRaises(ValidationError):
            self._allocate(second, amount=300.0)

    def test_06_wrong_partner(self):
        other = self.env["res.partner"].create({
            "name": "DepositPro Other Customer"})
        other_invoice = self._make_invoice(other, 200.0)
        deposit = self._deposit(500.0)
        with self.assertRaises(ValidationError):
            self._allocate(deposit, invoice=other_invoice, amount=100.0)
        self.assertEqual(deposit.state, "confirmed")

    def test_07_refund_remaining(self):
        deposit = self._deposit(500.0)
        deposit.action_refund()
        self.assertEqual(deposit.state, "refunded")
        self.assertAlmostEqual(deposit.refund_amount, 500.0, places=2)
        self.assertAlmostEqual(deposit.remaining_amount, 0.0, places=2)
        self.assertTrue(deposit.refund_date)
        with self.assertRaises(UserError):
            deposit.action_refund()

    def test_08_cancel_with_allocation(self):
        deposit = self._deposit(500.0)
        allocation = self._allocate(deposit, amount=100.0)
        self.assertEqual(deposit.state, "partial")
        with self.assertRaises(UserError):
            deposit.action_cancel()
        allocation.unlink()
        self.assertEqual(deposit.state, "confirmed")
        deposit.action_cancel()
        self.assertEqual(deposit.state, "cancelled")
        deposit.action_reset()
        self.assertEqual(deposit.state, "draft")
