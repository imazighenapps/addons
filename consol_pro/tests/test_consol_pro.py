# -*- coding: utf-8 -*-
from datetime import date
from unittest import SkipTest

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged
# ---SPLIT2---
@tagged("post_install", "-at_install")
class TestConsolPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Fully hermetic: the consolidation is computed on two fresh com-
        # panies so it can never pick up demo data posted by other modules.
        cls.company1 = cls.env["res.company"].create({
            "name": "ConsolPro Test Company A",
        })
        cls.company2 = cls.env["res.company"].create({
            "name": "ConsolPro Test Company B",
        })
        cls.expense_account = cls._account(
            cls.company1, "expense", "CON.1.EXP")
        cls.income_account = cls._account(
            cls.company1, "income", "CON.1.INC")
        cls.zero_account = cls._account(
            cls.company1, "expense", "CON.1.ZRO")
        cls.expense_account2 = cls._account(
            cls.company2, "expense", "CON.2.EXP")
        cls.income_account2 = cls._account(
            cls.company2, "income", "CON.2.INC")
        cls._move(cls.company1, "CON.-A", date(2026, 2, 10), [
            (cls.expense_account, 800.0, 0.0),
            (cls.income_account, 0.0, 800.0),
        ])
        cls._move(cls.company1, "CON.-B", date(2026, 3, 20), [
            (cls.expense_account, 300.0, 0.0),
            (cls.income_account, 0.0, 300.0),
        ])
        cls._move(cls.company1, "CON.-C", date(2026, 4, 15), [
            (cls.zero_account, 120.0, 0.0),
            (cls.zero_account, 0.0, 120.0),
        ])
        cls._move(cls.company2, "CON.-D", date(2026, 2, 5), [
            (cls.expense_account2, 200.0, 0.0),
            (cls.income_account2, 0.0, 200.0),
        ])
        cls.run_main = cls.env["consol.run"].create({
            "name": "ConsolPro Test Run",
            "date_from": date(2026, 1, 1),
            "date_to": date(2026, 6, 30),
            "company_ids": [Command.set([
                cls.company1.id, cls.company2.id])],
        })

    @classmethod
    def _account(cls, company, account_type, code):
        # company-dependent codes must be written with the target company
        # in the environment (Odoo 18.0 stores them per company root).
        return cls.env["account.account"].with_company(company).create({
            "name": "ConsolPro Test %s" % code,
            "code": code,
            "account_type": account_type,
            "company_ids": [Command.set(company.ids)],
        })

    @classmethod
    def _move(cls, company, ref, when, lines):
        journal = cls.env["account.journal"].search([
            ("type", "=", "general"),
            ("company_id", "=", company.id),
        ], limit=1)
        if not journal:
            journal = cls.env["account.journal"].create({
                "name": "ConsolPro Test Journal %s" % company.id,
                "code": "CNJ%s" % company.id,
                "type": "general",
                "company_id": company.id,
            })
        move = cls.env["account.move"].create({
            "company_id": company.id,
            "journal_id": journal.id,
            "move_type": "entry",
            "ref": ref,
            "date": when,
            "line_ids": [
                Command.create({
                    "account_id": account.id,
                    "name": ref,
                    "debit": debit,
                    "credit": credit,
                })
                for account, debit, credit in lines
            ],
        })
        move.action_post()
        return move

    def _run(self, companies, **kwargs):
        values = {
            "date_from": date(2026, 1, 1),
            "date_to": date(2026, 6, 30),
            "company_ids": [Command.set([c.id for c in companies])],
        }
        values.update(kwargs)
        return self.env["consol.run"].create(values)

    def _line(self, run, company, account):
        lines = run.line_ids.filtered(
            lambda line: line.company_id == company
            and line.account_code == account.with_company(company).code)
        self.assertEqual(len(lines), 1)
        return lines

    def test_01_compute_aggregates_by_company_and_account(self):
        self.assertEqual(self.run_main.state, "draft")
        self.assertTrue(self.run_main.action_compute())
        self.assertEqual(self.run_main.state, "computed")
        self.assertEqual(len(self.run_main.line_ids), 4)
        expense1 = self._line(self.run_main, self.company1, self.expense_account)
        income1 = self._line(self.run_main, self.company1, self.income_account)
        expense2 = self._line(self.run_main, self.company2,
                              self.expense_account2)
        income2 = self._line(self.run_main, self.company2, self.income_account2)
        self.assertFalse(self.run_main.line_ids.filtered(
            lambda line: line.account_code ==
            self.zero_account.with_company(self.company1).code))
        self.assertEqual(expense1.account_name, "ConsolPro Test CON.1.EXP")
        self.assertAlmostEqual(expense1.debit, 1100.0, places=2)
        self.assertAlmostEqual(expense1.credit, 0.0, places=2)
        self.assertAlmostEqual(income1.debit, 0.0, places=2)
        self.assertAlmostEqual(income1.credit, 1100.0, places=2)
        self.assertAlmostEqual(expense2.debit, 200.0, places=2)
        self.assertAlmostEqual(income2.credit, 200.0, places=2)
        self.assertFalse(expense1.eliminated)
        single = self._run([self.company1])
        self.assertTrue(single.action_compute())
        self.assertEqual(len(single.line_ids), 2)
        self.assertFalse(single.line_ids.filtered(
            lambda line: line.company_id == self.company2))
        self.assertTrue(
            single.line_ids.mapped("company_id") == self.company1)

    def test_02_totals_are_the_sums_of_the_lines(self):
        self.assertTrue(self.run_main.action_compute())
        self.run_main.invalidate_recordset()
        self.assertAlmostEqual(self.run_main.total_debit, 1300.0, places=2)
        self.assertAlmostEqual(self.run_main.total_credit, 1300.0, places=2)
        income1 = self._line(self.run_main, self.company1, self.income_account)
        income1.write({"debit": 100.0})
        self.run_main.invalidate_recordset()
        self.assertAlmostEqual(self.run_main.total_debit, 1400.0, places=2)

    def test_03_balance_is_debit_minus_credit(self):
        self.assertTrue(self.run_main.action_compute())
        for line in self.run_main.line_ids:
            self.assertAlmostEqual(
                line.balance, line.debit - line.credit, places=2)
        self.assertAlmostEqual(
            self._line(
                self.run_main, self.company1, self.expense_account).balance,
            1100.0, places=2)
        self.assertAlmostEqual(
            self._line(
                self.run_main, self.company1, self.income_account).balance,
            -1100.0, places=2)

    def test_04_eliminate_zeroes_the_mapped_lines(self):
        self.assertTrue(self.run_main.action_compute())
        income1 = self._line(self.run_main, self.company1, self.income_account)
        expense2 = self._line(self.run_main, self.company2,
                              self.expense_account2)
        income1.write({"mapping": "IC-SALES"})
        expense2.write({"mapping": "IC-PURCH"})
        fresh = self._run([self.company1])
        self.assertTrue(fresh.action_compute())
        with self.assertRaises(UserError):
            fresh.action_eliminate()
        self.assertTrue(self.run_main.action_eliminate())
        self.assertTrue(income1.eliminated)
        self.assertTrue(expense2.eliminated)
        self.assertAlmostEqual(income1.debit, 0.0, places=2)
        self.assertAlmostEqual(income1.credit, 0.0, places=2)
        self.assertAlmostEqual(income1.balance, 0.0, places=2)
        expense1 = self._line(self.run_main, self.company1, self.expense_account)
        self.assertFalse(expense1.eliminated)
        self.assertAlmostEqual(expense1.debit, 1100.0, places=2)
        self.run_main.invalidate_recordset()
        self.assertAlmostEqual(self.run_main.total_debit, 1100.0, places=2)
        self.assertAlmostEqual(self.run_main.total_credit, 200.0, places=2)
        with self.assertRaises(UserError):
            self.run_main.action_eliminate()
# ---SPLIT3---
    def test_05_compute_on_an_empty_period(self):
        empty = self._run(
            [self.company1],
            date_from=date(2030, 1, 1),
            date_to=date(2030, 12, 31),
        )
        self.assertTrue(empty.action_compute())
        self.assertEqual(empty.state, "computed")
        self.assertFalse(empty.line_ids)
        empty.invalidate_recordset()
        self.assertAlmostEqual(empty.total_debit, 0.0, places=2)
        self.assertAlmostEqual(empty.total_credit, 0.0, places=2)

    def test_06_dates_and_duplicates_are_validated(self):
        with self.assertRaises(ValidationError):
            self._run(
                [self.company1],
                date_from=date(2026, 6, 30),
                date_to=date(2026, 1, 1),
            )
        self.assertTrue(self.run_main.action_compute())
        with self.assertRaises(ValidationError):
            self.run_main.write({"date_to": date(2025, 12, 31)})
        with self.assertRaises(ValidationError):
            self._run([self.company1], name="ConsolPro Test Run")
        values = {
            "name": "ConsolPro Test Twice",
            "date_from": date(2026, 1, 1),
            "date_to": date(2026, 2, 28),
            "company_ids": [Command.set([self.company1.id])],
        }
        with self.assertRaises(ValidationError):
            self.env["consol.run"].create([dict(values), dict(values)])
        sequenced = self._run([self.company1])
        self.assertTrue(sequenced.name.startswith("CON/"))
        other = self._run([self.company1])
        self.assertNotEqual(sequenced.name, other.name)

    def test_07_post_locks_the_run(self):
        self.assertTrue(self.run_main.action_compute())
        income1 = self._line(self.run_main, self.company1, self.income_account)
        income1.write({"mapping": "IC"})
        self.assertTrue(self.run_main.action_post())
        self.assertEqual(self.run_main.state, "posted")
        with self.assertRaises(UserError):
            self.run_main.action_compute()
        with self.assertRaises(UserError):
            self.run_main.action_eliminate()
        with self.assertRaises(UserError):
            income1.write({"debit": 5.0})
        with self.assertRaises(UserError):
            self.env["consol.line"].create({
                "run_id": self.run_main.id,
                "company_id": self.company1.id,
                "account_code": "CON.1.NEW",
                "debit": 1.0,
            })
        with self.assertRaises(UserError):
            income1.unlink()
        with self.assertRaises(UserError):
            self.run_main.action_post()
        with self.assertRaises(UserError):
            self.run_main.write({"date_from": date(2025, 1, 1)})
        self.assertTrue(self.run_main.action_reset())
        self.assertEqual(self.run_main.state, "draft")
        self.assertTrue(self.run_main.action_compute())
        self.assertEqual(self.run_main.state, "computed")

    def test_08_reset_returns_to_draft(self):
        run = self._run([self.company1])
        with self.assertRaises(UserError):
            run.action_reset()
        self.assertTrue(run.action_compute())
        income1 = self._line(run, self.company1, self.income_account)
        income1.write({"mapping": "IC"})
        self.assertTrue(run.action_eliminate())
        self.assertTrue(income1.eliminated)
        expense1 = self._line(run, self.company1, self.expense_account)
        expense1.write({"mapping": "MAP"})
        self.assertTrue(run.action_compute())
        self.assertEqual(
            self._line(
                run, self.company1, self.expense_account).mapping, "MAP")
        kept = self._line(run, self.company1, self.income_account)
        self.assertTrue(kept.eliminated)
        self.assertAlmostEqual(kept.credit, 0.0, places=2)
        self.assertTrue(run.action_reset())
        self.assertEqual(run.state, "draft")
        self.assertFalse(run.line_ids)
        self.assertTrue(run.action_compute())
        income1 = self._line(run, self.company1, self.income_account)
        self.assertFalse(income1.eliminated)
        self.assertAlmostEqual(income1.credit, 1100.0, places=2)
