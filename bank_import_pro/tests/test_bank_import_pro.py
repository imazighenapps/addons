# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged

CSV_STATEMENT = (
    "2026-01-05;ACME invoice 101;INV-101;125.50\n"
    "2026-01-06;Bank fees of the month;FEES;-12.30\n"
    "2026-01-07;Unknown supplier delivery;S-77;88.00\n"
)
CSV_DUPLICATE = (
    "2026-03-10;Duplicate check transaction;DUP-1;55.00\n"
)
CSV_RETRY = (
    "2026-03-10;Duplicate check transaction;DUP-1;55.00\n"
    "2026-03-11;Something else today;OTH-2;10.00\n"
)
CSV_IDEMPOTENT = (
    "2026-04-02;Zeta logistics monthly;LOG-9;200.00\n"
)
CAMT_STATEMENT = (
    "<stmt><stmt-entries>"
    "<entry><date>2026-02-01</date>"
    "<credit-debit-indicator>CRDT</credit-debit-indicator>"
    "<amount>250.00</amount><ref>PAY-1</ref>"
    "<nav-info>ACME settlement</nav-info></entry>"
    "<entry><date>2026-02-02</date>"
    "<credit-debit-indicator>DBIT</credit-debit-indicator>"
    "<amount>40.00</amount><ref>FEE-2</ref>"
    "<nav-info>Card fees</nav-info></entry>"
    "</stmt-entries></stmt>"
)


@tagged("post_install", "-at_install")
class TestBankImportPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_acme = cls.env["res.partner"].create({
            "name": "BankImport Test Supplier ACME", "supplier_rank": 1})
        cls.partner_other = cls.env["res.partner"].create({
            "name": "BankImport Test Supplier Other", "supplier_rank": 1})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "bank"),
             ("company_id", "=", cls.env.company.id)], limit=1)
        if not cls.journal:
            try:
                cls.journal = cls.env["account.journal"].create({
                    "name": "BankImport Test Bank", "code": "BNKB",
                    "type": "bank"})
            except Exception:
                cls.journal = cls.env["account.journal"]
        if not cls.journal:
            cls.skipTest("No bank journal available for BankImport tests.")
        cls.account = cls.env["account.account"].search(
            [("account_type", "=", "expense"),
             ("company_ids", "in", cls.env.company.id)], limit=1)
        if not cls.account:
            try:
                cls.account = cls.env["account.account"].create({
                    "name": "BankImport Test Expenses", "code": "671000",
                    "account_type": "expense"})
            except Exception:
                cls.account = cls.env["account.account"]
        rule_vals = {"name": "BankImport ACME Rule", "pattern": "acme",
                     "partner_id": cls.partner_acme.id, "sequence": 10}
        if cls.account:
            rule_vals["account_id"] = cls.account.id
        cls.rule_acme = cls.env["bank.import.rule"].create(rule_vals)
        cls.rule_supplier = cls.env["bank.import.rule"].create({
            "name": "BankImport Supplier Rule", "pattern": "supplier",
            "partner_id": cls.partner_other.id, "sequence": 20})

    def _batch(self, name, data, file_type="csv"):
        return self.env["bank.import.batch"].create({
            "name": name,
            "file_name": "%s.%s" % (name, file_type),
            "file_type": file_type,
            "raw_data": data,
            "journal_id": self.journal.id,
        })

    def test_01_parse_csv_creates_lines(self):
        batch = self._batch("csv-parse", CSV_STATEMENT)
        self.assertEqual(batch.state, "draft")
        self.assertTrue(batch.action_parse())
        self.assertEqual(batch.state, "imported")
        self.assertFalse(batch.error_message)
        self.assertEqual(len(batch.line_ids), 3)
        first = batch.line_ids[0]
        self.assertEqual(first.label, "ACME invoice 101")
        self.assertEqual(first.reference, "INV-101")
        self.assertEqual(first.date, date(2026, 1, 5))
        self.assertEqual(len(self.env["bank.import.line"].search(
            [("batch_id", "=", batch.id)])), 3)

    def test_02_csv_amounts_are_signed(self):
        batch = self._batch("csv-signed", CSV_STATEMENT)
        batch.action_parse()
        amounts = batch.line_ids.mapped("amount")
        self.assertIn(125.50, amounts)
        self.assertIn(-12.30, amounts)
        self.assertIn(88.00, amounts)
        fees = batch.line_ids.filtered(
            lambda line: line.reference == "FEES")
        self.assertEqual(fees.amount, -12.30)

    def test_03_parse_camt_statement(self):
        batch = self._batch("camt-parse", CAMT_STATEMENT, file_type="camt")
        self.assertTrue(batch.action_parse())
        self.assertEqual(batch.state, "imported")
        self.assertEqual(len(batch.line_ids), 2)
        credit = batch.line_ids.filtered(
            lambda line: line.reference == "PAY-1")
        debit = batch.line_ids.filtered(
            lambda line: line.reference == "FEE-2")
        self.assertEqual(credit.amount, 250.00)
        self.assertEqual(debit.amount, -40.00)
        self.assertEqual(credit.label, "ACME settlement")
        self.assertEqual(credit.date, date(2026, 2, 1))

    def test_04_rules_assign_partner_and_account(self):
        batch = self._batch("csv-rules", CSV_STATEMENT)
        batch.action_parse()
        self.assertTrue(batch.action_apply_rules())
        acme = batch.line_ids.filtered(
            lambda line: line.label == "ACME invoice 101")
        supplier = batch.line_ids.filtered(
            lambda line: line.label == "Unknown supplier delivery")
        fees = batch.line_ids.filtered(
            lambda line: line.label == "Bank fees of the month")
        self.assertTrue(acme.matched)
        self.assertEqual(acme.partner_id, self.partner_acme)
        if self.account:
            self.assertEqual(acme.account_id, self.account)
        self.assertTrue(supplier.matched)
        self.assertEqual(supplier.partner_id, self.partner_other)
        self.assertFalse(fees.matched)
        self.assertFalse(fees.partner_id)

    def test_05_duplicate_detection(self):
        batch_one = self._batch("dup-first", CSV_DUPLICATE)
        batch_one.action_parse()
        first_line = batch_one.line_ids
        self.assertFalse(first_line.duplicate)
        batch_two = self._batch("dup-second", CSV_RETRY)
        batch_two.action_parse()
        self.assertTrue(batch_two.action_flag_duplicates())
        duplicated = batch_two.line_ids.filtered(
            lambda line: line.reference == "DUP-1")
        other = batch_two.line_ids.filtered(
            lambda line: line.reference == "OTH-2")
        self.assertTrue(duplicated.duplicate)
        self.assertFalse(other.duplicate)
        self.assertFalse(first_line.duplicate)

    def test_06_total_amount_equals_sum_of_lines(self):
        batch = self._batch("camt-total", CAMT_STATEMENT, file_type="camt")
        batch.action_parse()
        self.assertAlmostEqual(batch.total_amount, 210.00, places=2)
        batch_csv = self._batch("csv-total", CSV_STATEMENT)
        batch_csv.action_parse()
        csv_total = (125.50 + (-12.30) + 88.00) or 0.0
        self.assertAlmostEqual(batch_csv.total_amount, csv_total, places=2)
        self.assertAlmostEqual(
            batch_csv.total_amount,
            sum(batch_csv.line_ids.mapped("amount")), places=2)

    def test_07_invalid_content_sets_error_state(self):
        batch_header = self._batch(
            "csv-no-rows", "date;label;reference;amount\n")
        self.assertTrue(batch_header.action_parse())
        self.assertEqual(batch_header.state, "error")
        self.assertTrue(batch_header.error_message)
        self.assertFalse(batch_header.line_ids)
        batch_xml = self._batch(
            "camt-broken", "<stmt><broken", file_type="camt")
        self.assertTrue(batch_xml.action_parse())
        self.assertEqual(batch_xml.state, "error")
        self.assertIn("failed", batch_xml.error_message)
        self.assertFalse(batch_xml.line_ids)

    def test_08_apply_rules_is_idempotent(self):
        self.env["bank.import.rule"].create({
            "name": "BankImport Zeta Rule", "pattern": "zeta",
            "partner_id": self.partner_acme.id, "sequence": 5})
        batch = self._batch("csv-idempotent", CSV_IDEMPOTENT)
        batch.action_parse()
        self.assertTrue(batch.action_apply_rules())
        line = batch.line_ids
        self.assertTrue(line.matched)
        self.assertEqual(line.partner_id, self.partner_acme)
        first_partner = line.partner_id
        # a new, higher-priority rule must not steal an already matched line
        self.env["bank.import.rule"].create({
            "name": "BankImport Monthly Rule", "pattern": "monthly",
            "partner_id": self.partner_other.id, "sequence": 1})
        self.assertTrue(batch.action_apply_rules())
        self.assertEqual(line.partner_id, first_partner)
        self.assertTrue(line.matched)
        self.assertNotEqual(line.partner_id, self.partner_other)
