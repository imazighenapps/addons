# -*- coding: utf-8 -*-
import re

from psycopg2 import IntegrityError

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged

PAYABLE_REPLACEMENT = (
    r'(cbc:PayableAmount currencyID="[A-Z]+">)[0-9.]+(<)')
STALE_TOTAL = r"\g<1>999.99\g<2>"


@tagged("post_install", "-at_install")
class TestEinvoiceValidatePro(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Fully hermetic: a dedicated NON-French company so the installed
        # fr_einvoicing_pack (never imported nor modified here) does not
        # intercept the posting of the test invoices.
        cls.company = cls.env["res.company"].create({
            "name": "EINV Test Company",
            "country_id":
                cls.env["res.country"].search([("code", "=", "US")],
                                              limit=1).id,
        })
        cls.partner = cls.env["res.partner"].create({
            "name": "EINV Test Customer",
            # A VAT number so the module's MISSING_TAX check has something
            # to bite on; the pack ignores it (partner is not French).
            "vat": "FR42123456789",
        })
        cls.product = cls.env["product.product"].create({
            "name": "EINV Test Service",
            "type": "service",
            "list_price": 100.0,
        })
        cls.receivable = cls.env["account.account"].create({
            "name": "EINV Receivable", "code": "EINVREC",
            "account_type": "asset_receivable", "reconcile": True,
            "company_ids": [Command.set(cls.company.ids)],
        })
        cls.income = cls.env["account.account"].create({
            "name": "EINV Income", "code": "EINVINC",
            "account_type": "income",
            "company_ids": [Command.set(cls.company.ids)],
        })
        cls.tax_account = cls.env["account.account"].create({
            "name": "EINV Tax Account", "code": "EINVTAX",
            "account_type": "expense",
            "company_ids": [Command.set(cls.company.ids)],
        })
        cls.journal = cls.env["account.journal"].create({
            "name": "EINV Sale Journal", "code": "EINVSJ",
            "type": "sale", "company_id": cls.company.id,
        })
        cls.partner.with_company(cls.company).property_account_receivable_id \
            = cls.receivable.id
        cls.tax_group = cls.env["account.tax.group"].search([
            ("company_id", "=", cls.company.id)], limit=1)
        if not cls.tax_group:
            cls.tax_group = cls.env["account.tax.group"].create({
                "name": "EINV Test VAT Group",
                "company_id": cls.company.id,
            })
        cls.tax = cls.env["account.tax"].create({
            "name": "EINV Test VAT 20%",
            "amount_type": "percent",
            "amount": 20.0,
            "type_tax_use": "sale",
            "company_id": cls.company.id,
            "tax_group_id": cls.tax_group.id,
        })
        cls.tax.invoice_repartition_line_ids.filtered(
            lambda line: line.repartition_type == "tax"
        ).write({"account_id": cls.tax_account.id})

    def _invoice(self, with_tax=True, post=True, **kwargs):
        line_vals = {
            "product_id": self.product.id,
            "name": "EINV Test Line",
            "quantity": 2.0,
            "price_unit": 100.0,
            "account_id": self.income.id,
        }
        if with_tax and self.tax:
            line_vals["tax_ids"] = [Command.set(self.tax.ids)]
        vals = {
            "move_type": "out_invoice",
            "company_id": self.company.id,
            "journal_id": self.journal.id,
            "partner_id": self.partner.id,
            "invoice_date": "2026-03-01",
            "invoice_line_ids": [Command.create(line_vals)],
        }
        vals.update(kwargs)
        invoice = self.env["account.move"].create(vals)
        if post:
            invoice.action_post()
        return invoice

    def _check(self, invoice, **kwargs):
        vals = {
            "invoice_id": invoice.id,
            "company_id": invoice.company_id.id,
        }
        vals.update(kwargs)
        return self.env["einvoice.check"].create(vals)

    def test_01_generate_requires_a_posted_invoice(self):
        invoice = self._invoice(post=False)
        check = self._check(invoice)
        self.assertEqual(check.state, "draft")
        self.assertFalse(check.xml_data)
        with self.assertRaises(UserError):
            check.action_generate()
        with self.assertRaises(UserError):
            check.action_validate()
        self.assertEqual(check.state, "draft")
        self.assertFalse(check.xml_data)
        self.assertEqual(check.issue_count, 0)

    def test_02_xml_contains_the_invoice_data(self):
        invoice = self._invoice()
        check = self._check(invoice, format="ubl")
        self.assertTrue(check.action_generate())
        self.assertEqual(check.state, "generated")
        xml = check.xml_data
        self.assertIn("cbc:ID>%s<" % invoice.name, xml)
        self.assertIn(str(invoice.invoice_date), xml)
        self.assertIn(invoice.currency_id.name, xml)
        self.assertIn(invoice.partner_id.name, xml)
        self.assertIn(invoice.company_id.name, xml)
        self.assertIn("%.2f" % invoice.amount_total, xml)
        self.assertIn("%.2f" % invoice.amount_untaxed, xml)
        self.assertEqual(check.issue_count, 0)

    def test_03_missing_tax_on_vat_customer(self):
        invoice = self._invoice(with_tax=False)
        check = self._check(invoice)
        check.action_generate()
        self.assertTrue(check.action_validate())
        self.assertEqual(check.state, "invalid")
        issue = check.issue_ids.filtered(
            lambda one: one.code == "MISSING_TAX")
        self.assertEqual(len(issue), 1)
        self.assertEqual(issue.severity, "error")
        self.assertEqual(issue.field_name, "tax_ids")
        self.assertEqual(check.issue_count, 1)

    def test_04_total_mismatch_in_xml(self):
        invoice = self._invoice(with_tax=True)
        check = self._check(invoice)
        check.action_generate()
        check.xml_data = re.sub(
            PAYABLE_REPLACEMENT, STALE_TOTAL, check.xml_data)
        self.assertTrue(check.action_validate())
        self.assertEqual(check.state, "invalid")
        mismatch = check.issue_ids.filtered(
            lambda one: one.code == "TOTAL_MISMATCH")
        self.assertEqual(len(mismatch), 1)
        self.assertEqual(mismatch.severity, "error")
        self.assertEqual(check.issue_count, 1)

    def test_05_valid_invoice_is_valid(self):
        invoice = self._invoice(with_tax=True)
        check = self._check(invoice, format="facturx")
        check.action_generate()
        self.assertTrue(check.action_validate())
        self.assertEqual(check.state, "valid")
        self.assertFalse(check.issue_ids.filtered(
            lambda one: one.severity == "error"))
        self.assertEqual(check.issue_count, 0)

    def test_06_issue_count_on_two_errors(self):
        invoice = self._invoice(with_tax=False)
        check = self._check(invoice)
        check.action_generate()
        check.xml_data = re.sub(
            PAYABLE_REPLACEMENT, STALE_TOTAL, check.xml_data)
        check.action_validate()
        self.assertEqual(check.issue_count, 2)
        found = check.issue_ids.search([("check_id", "=", check.id)])
        self.assertEqual(len(found), 2)
        self.assertEqual(
            len(found.filtered(
                lambda one: one.severity == "error")), 2)
        self.assertIn("MISSING_TAX", found.mapped("code"))
        self.assertIn("TOTAL_MISMATCH", found.mapped("code"))

    def test_07_warning_severity_keeps_the_check_valid(self):
        invoice = self._invoice(with_tax=True)
        check = self._check(invoice)
        check.action_generate()
        check.xml_data = check.xml_data.replace(
            "cbc:ID>%s<" % invoice.name, "cbc:ID>REF-STALE<", 1)
        self.assertTrue(check.action_validate())
        self.assertEqual(check.state, "valid")
        self.assertEqual(len(check.issue_ids), 1)
        issue = check.issue_ids
        self.assertEqual(issue.severity, "warning")
        self.assertEqual(issue.code, "XML_REF_MISMATCH")
        self.assertEqual(check.issue_count, 1)

    def test_08_reset_clears_everything_and_bill_refused(self):
        check = self._check(self._invoice(with_tax=False))
        self.assertTrue(check.action_generate())
        check.action_validate()
        self.assertEqual(check.state, "invalid")
        self.assertTrue(check.issue_ids)
        self.assertTrue(check.action_reset())
        self.assertEqual(check.state, "draft")
        self.assertFalse(check.issue_ids)
        self.assertFalse(check.xml_data)
        self.assertEqual(check.issue_count, 0)
        with self.assertRaises(UserError):
            check.action_reset()
        self.assertTrue(check.action_generate())
        self.assertEqual(check.state, "generated")
        other = self._check(self._invoice())
        # The uniqueness rule is a SQL constraint: only the flush raises,
        # and the error class differs between Odoo 18/19 and 20.
        try:
            with self.env.cr.savepoint():
                other.name = check.name
                other.flush_recordset()
        except (ValidationError, IntegrityError):
            pass
        else:
            self.fail("A duplicate check reference was accepted.")
        bill = self.env["account.move"].create({
            "move_type": "in_invoice",
            "partner_id": self.partner.id,
            "invoice_line_ids": [Command.create({
                "product_id": self.product.id,
                "name": "EINV Test Bill Line",
                "quantity": 1.0,
                "price_unit": 50.0,
                # No tax: product default taxes belong to another fiscal
                # country and would be refused by account.move.
                "tax_ids": [Command.set([])],
            })],
        })
        with self.assertRaises(ValidationError):
            self._check(bill)
