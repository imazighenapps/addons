# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStatementPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Statement Test Customer", "is_company": True})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "general")], limit=1)
        cls.receivable = cls.partner.property_account_receivable_id
        cls.income = cls.env["account.account"].search(
            [("account_type", "=", "income"),
             ("company_ids", "in", cls.env.company.id)], limit=1)

    def _move(self, debit, move_date, label="Entry"):
        move = self.env["account.move"].create({
            "move_type": "entry",
            "journal_id": self.journal.id,
            "date": move_date,
            "line_ids": [
                (0, 0, {"account_id": self.receivable.id,
                        "partner_id": self.partner.id,
                        "debit": debit, "credit": 0.0, "name": label}),
                (0, 0, {"account_id": self.income.id,
                        "partner_id": self.partner.id,
                        "debit": 0.0, "credit": debit, "name": label}),
            ],
        })
        move.action_post()
        return move

    def _statement(self, date_from=date(2026, 1, 1), date_to=date(2026, 12, 31)):
        return self.env["statement.run"].create({
            "partner_id": self.partner.id,
            "date_from": date_from,
            "date_to": date_to,
        })

    def test_01_sequence(self):
        statement = self._statement()
        self.assertTrue(statement.name.startswith("STM/"))

    def test_02_generate_with_opening(self):
        self._move(200.0, date(2025, 12, 15), "Opening")
        self._move(500.0, date(2026, 3, 10), "Invoice 1")
        statement = self._statement()
        statement.action_generate()
        self.assertAlmostEqual(statement.opening_balance, 200.0, places=2)
        self.assertAlmostEqual(statement.total_debit, 500.0, places=2)
        self.assertAlmostEqual(statement.closing_balance, 700.0, places=2)
        self.assertEqual(statement.line_count, 1)

    def test_03_credit_movement(self):
        self._move(500.0, date(2026, 2, 1))
        # Payment: credit the receivable
        move = self.env["account.move"].create({
            "move_type": "entry", "journal_id": self.journal.id,
            "date": date(2026, 2, 20),
            "line_ids": [
                (0, 0, {"account_id": self.receivable.id,
                        "partner_id": self.partner.id,
                        "debit": 0.0, "credit": 120.0, "name": "Payment"}),
                (0, 0, {"account_id": self.income.id,
                        "partner_id": self.partner.id,
                        "debit": 120.0, "credit": 0.0, "name": "Payment"}),
            ]})
        move.action_post()
        statement = self._statement(date_from=date(2026, 1, 1),
                                    date_to=date(2026, 12, 31))
        statement.action_generate()
        self.assertAlmostEqual(statement.total_credit, 120.0, places=2)
        self.assertAlmostEqual(statement.closing_balance, 380.0, places=2)

    def test_04_send(self):
        self._move(100.0, date(2026, 4, 1))
        statement = self._statement()
        statement.action_generate()
        statement.action_send()
        self.assertEqual(statement.state, "sent")
        self.assertTrue(statement.sent_date)

    def test_05_batch_wizard(self):
        self._move(100.0, date(2026, 5, 1))
        wizard = self.env["statement.batch"].create({
            "date_from": date(2026, 1, 1),
            "date_to": date(2026, 12, 31),
            "partner_ids": [(6, 0, [self.partner.id])],
        })
        action = wizard.action_generate()
        self.assertEqual(action["res_model"], "statement.run")
        self.assertTrue(action["domain"])

    def test_06_pdf_report(self):
        self._move(100.0, date(2026, 6, 1))
        statement = self._statement()
        statement.action_generate()
        report = self.env.ref("statement_pro.action_report_statement")
        try:
            pdf, _ext = report._render_qweb_pdf(
                "statement_pro.report_statement", res_ids=statement.ids)
        except TypeError:
            pdf, _ext = report._render_qweb_pdf(statement.ids)
        self.assertTrue(pdf)
        head = pdf[:400].lower()
        self.assertTrue(head.startswith(b"%pdf") or b"<html" in head,
                        "Unexpected report output: %r" % pdf[:120])
