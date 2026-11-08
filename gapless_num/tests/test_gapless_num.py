# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGaplessNum(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Gapless Test Customer", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "Gapless Test Product", "type": "service",
            "list_price": 100.0})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", cls.env.company.id)],
            limit=1)

    def _invoice(self, name):
        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "journal_id": self.journal.id,
            "invoice_date": date(2099, 1, 10),
            "date": date(2099, 1, 10),
            "invoice_line_ids": [(0, 0, {
                "product_id": self.product.id,
                "quantity": 1.0,
                "price_unit": 100.0,
            })],
        })
        move.action_post()
        self.env.cr.execute(
            "UPDATE account_move SET name = %s WHERE id = %s",
            (name, move.id))
        move.invalidate_recordset()
        self.assertEqual(move.name, name)
        return move

    def _rule(self, **kwargs):
        values = {
            "name": "Gapless Rule",
            "company_id": self.env.company.id,
            "journal_id": self.journal.id,
            "mode": "warn",
        }
        values.update(kwargs)
        return self.env["gapless.rule"].create(values)

    def _scan(self, rule=None):
        scan = self.env["gapless.scan"].create({
            "date_from": date(2099, 1, 1),
            "date_to": date(2099, 1, 31),
            "rule_id": rule.id if rule else False,
        })
        scan.action_run()
        return self.env["gapless.issue"].search([
            ("journal_id", "=", self.journal.id),
            ("issue_date", ">=", date(2099, 1, 1)),
        ])

    def test_01_detects_a_gap(self):
        self._rule()
        self._invoice("INV/2099/00001")
        self._invoice("INV/2099/00003")
        issues = self._scan()
        gaps = issues.filtered(lambda i: i.kind == "gap")
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps.expected, "INV/2099/00002")

    def test_02_continuous_sequence_has_no_gap(self):
        self._rule()
        self._invoice("INV/2099/00001")
        self._invoice("INV/2099/00002")
        issues = self._scan()
        self.assertFalse(issues.filtered(lambda i: i.kind == "gap"))

    def test_03_detects_a_duplicate(self):
        self._rule()
        first = self._invoice("INV/2099/00001")
        second = self._invoice("INV/2099/00002")
        # Core refuses two posted entries with the same name per journal, so
        # the duplicate can only be simulated on a database that lost the
        # index (restore, manual import). The DDL is rolled back with the
        # test transaction.
        self.env.cr.execute("DROP INDEX IF EXISTS account_move_unique_name")
        self.env.cr.execute(
            "UPDATE account_move SET name = %s WHERE id = %s",
            ("INV/2099/00001", second.id))
        self.env.invalidate_all()
        issues = self._scan()
        duplicates = issues.filtered(lambda i: i.kind == "duplicate")
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates.move_name, "INV/2099/00001")
        self.assertIn(first.name, ("INV/2099/00001",))

    def test_04_block_mode_refuses_manual_rename(self):
        move = self._invoice("INV/2099/00005")
        self._rule(mode="block")
        with self.assertRaises(UserError):
            move.write({"name": "INV/2099/00099"})

    def test_05_warn_mode_traces_manual_rename(self):
        move = self._invoice("INV/2099/00005")
        self._rule(mode="warn")
        before = self.env["gapless.issue"].search_count([
            ("kind", "=", "manual"), ("move_id", "=", move.id)])
        move.write({"name": "INV/2099/00099"})
        after = self.env["gapless.issue"].search_count([
            ("kind", "=", "manual"), ("move_id", "=", move.id)])
        self.assertEqual(after, before + 1)
        issue = self.env["gapless.issue"].search([
            ("kind", "=", "manual"), ("move_id", "=", move.id)], limit=1)
        self.assertEqual(issue.found, "INV/2099/00099")

    def test_06_scan_is_idempotent(self):
        self._rule()
        self._invoice("INV/2099/00001")
        self._invoice("INV/2099/00004")
        first = len(self._scan())
        second = len(self._scan())
        self.assertEqual(first, second)

    def test_07_anomaly_workflow(self):
        self._rule()
        self._invoice("INV/2099/00001")
        self._invoice("INV/2099/00003")
        issue = self._scan().filtered(lambda i: i.kind == "gap")[:1]
        self.assertTrue(issue.action_resolve())
        self.assertEqual(issue.state, "resolved")
        self.assertTrue(issue.action_ignore())
        self.assertEqual(issue.state, "ignored")
        self.assertTrue(issue.action_reopen())
        self.assertEqual(issue.state, "open")

    def test_08_company_isolation(self):
        other = self.env["res.company"].create({
            "name": "Gapless Other Company"})
        move = self._invoice("INV/2099/00021")
        rule = self.env["gapless.rule"].create({
            "name": "Other Company Rule",
            "company_id": other.id,
            "mode": "block",
        })
        self.assertNotEqual(rule.company_id, move.company_id)
        move.write({"name": "INV/2099/00022"})
        self.assertEqual(move.name, "INV/2099/00022")
