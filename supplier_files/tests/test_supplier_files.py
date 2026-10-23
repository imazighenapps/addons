# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSupplierFiles(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Test Supplier Co", "is_company": True, "supplier_rank": 1,
        })
        # Accounts must live in setUpClass: anything created inside a test
        # method is rolled back before the next test runs.
        cls.expense = cls.env["account.account"].create({
            "name": "Test Expense SF", "code": "606SFILE",
            "account_type": "expense"})
        cls.payable = cls.env["account.account"].create({
            "name": "Test Payable SF", "code": "401SFILE",
            "account_type": "liability_payable"})
        cls.partner.property_account_payable_id = cls.payable.id
        cls.purchase_journal = cls.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1)

    def _type(self, code):
        return self.env["supplier.document.type"].search(
            [("code", "=", code)])[:1]

    def _doc(self, code, **kw):
        return self.env["supplier.document"].create({
            "partner_id": self.partner.id,
            "type_id": self._type(code).id, **kw})

    def _bill(self, price=100.0):
        return self.env["account.move"].create({
            "move_type": "in_invoice",
            "partner_id": self.partner.id,
            "journal_id": self.purchase_journal.id,
            "invoice_date": fields.Date.today(),
            "fiscal_position_id": False,
            "invoice_line_ids": [(0, 0, {
                "name": "Services", "quantity": 1.0, "price_unit": price})],
        })

    def test_01_seed_types(self):
        types = self.env["supplier.document.type"].search([])
        self.assertEqual(len(types), 6)
        self.assertTrue(types.filtered(lambda t: t.code == "REGISTRATION"))

    def test_02_sequence(self):
        doc = self._doc("VAT", reference="FR12345678901")
        self.assertTrue(doc.name.startswith("SD-"))

    def test_03_missing_blocks_file(self):
        rec = self.env["supplier.file.status"].evaluate_partner(self.partner)
        self.assertFalse(rec.complete)
        self.assertEqual(rec.score, 0)
        self.assertTrue(rec.blocking_ids)

    def test_04_complete_after_documents(self):
        for code in ("REGISTRATION", "VAT", "BANK"):
            self._doc(code, verified=True)
        rec = self.env["supplier.file.status"].evaluate_partner(self.partner)
        self.assertIn("INSURANCE", rec.missing_ids.mapped("code"))
        self.assertEqual(rec.score, 50)

    def test_05_expiry_state(self):
        soon = date.today() + timedelta(days=10)
        # use the record we just created: a global search by type code
        # would return every supplier's document and break ensure_one()
        doc = self._doc("INSURANCE", verified=True, expiry_date=soon)
        self.assertEqual(doc.state, "expiring")
        doc.expiry_date = date.today() - timedelta(days=1)
        self.assertEqual(doc.state, "expired")

    def test_06_payment_block(self):
        self.partner.supplier_block_payments = True
        self.assertTrue(self.partner.supplier_file_blocking)
        with self.assertRaises(UserError):
            self._bill().action_post()

    def test_07_no_block_when_off(self):
        self.partner.supplier_block_payments = False
        bill = self._bill()
        bill.action_post()
        self.assertEqual(bill.state, "posted")