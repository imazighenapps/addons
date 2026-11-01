# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFxRevalPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company_currency = cls.company.currency_id
        cls.foreign = cls._create_foreign_currency()
        cls.journal = cls.env["account.journal"].search([
            ("type", "=", "general"),
            ("company_id", "=", cls.company.id),
        ], limit=1)
        account_model = cls.env["account.account"]
        company_domain = [("company_ids", "in", cls.company.id)]
        cls.receivable_account = account_model.search(
            [("account_type", "=", "asset_receivable")] + company_domain,
            limit=1)
        cls.payable_account = account_model.search(
            [("account_type", "=", "liability_payable")] + company_domain,
            limit=1)
        cls.gain_account = account_model.search(
            [("account_type", "in", ["income", "income_other"])]
            + company_domain, limit=1)
        cls.loss_account = account_model.search(
            [("account_type", "in", ["expense", "expense_direct_cost"])]
            + company_domain, limit=1)
        customer_vals = {"name": "FxReval Test Customer"}
        if cls.receivable_account:
            customer_vals["property_account_receivable_id"] = \
                cls.receivable_account.id
        cls.customer = cls.env["res.partner"].create(customer_vals)
        supplier_vals = {"name": "FxReval Test Supplier"}
        if cls.payable_account:
            supplier_vals["property_account_payable_id"] = \
                cls.payable_account.id
        cls.supplier = cls.env["res.partner"].create(supplier_vals)

    @classmethod
    def _create_foreign_currency(cls):
        currency = cls.env["res.currency"].search(
            [("name", "=", "XTF")], limit=1)
        if not currency:
            currency = cls.env["res.currency"].create({
                "name": "XTF",
                "symbol": "X",
                "rounding": 0.01,
                "decimal_places": 2,
                "active": True,
            })
        rate = cls.env["res.currency.rate"].search([
            ("currency_id", "=", currency.id),
            ("company_id", "=", cls.company.id),
            ("name", "=", "2026-01-01"),
        ], limit=1)
        if not rate:
            cls.env["res.currency.rate"].create({
                "currency_id": currency.id,
                "name": "2026-01-01",
                "rate": 0.5,
                "company_id": cls.company.id,
            })
        return currency

    def _require_accounting(self):
        """Skip when the database has no journal or chart of accounts."""
        if not (self.journal and self.receivable_account
                and self.payable_account and self.gain_account
                and self.loss_account):
            self.skipTest(
                "No general journal or chart of accounts in this database.")

    def _open_item(self, partner, account, amount, currency=None,
                   move_date=None):
        """Post one open journal item, in the given currency."""
        currency = currency or self.foreign
        move_date = move_date or fields.Date.context_today(
            self.env["fx.revaluation"])
        company_amount = currency._convert(
            abs(amount), self.company_currency, self.company, move_date)
        debit = company_amount if amount > 0 else 0.0
        credit = 0.0 if amount > 0 else company_amount
        item = {
            "account_id": account.id,
            "partner_id": partner.id,
            "name": "Open item",
            "debit": debit,
            "credit": credit,
        }
        move_vals = {
            "move_type": "entry",
            "journal_id": self.journal.id,
            "date": move_date,
            "line_ids": [
                (0, 0, item),
                (0, 0, {
                    "account_id": self.gain_account.id,
                    "partner_id": partner.id,
                    "name": "Open item",
                    "debit": credit,
                    "credit": debit,
                }),
            ],
        }
        if currency != self.company_currency:
            item["currency_id"] = currency.id
            item["amount_currency"] = amount
            move_vals["currency_id"] = currency.id
        move = self.env["account.move"].create(move_vals)
        move.action_post()
        return move

    def _revaluation(self, **kwargs):
        values = {
            "currency_id": self.foreign.id,
            "rate": 1.0,
            "journal_id": self.journal.id if self.journal else False,
            "gain_account_id": (
                self.gain_account.id if self.gain_account else False),
            "loss_account_id": (
                self.loss_account.id if self.loss_account else False),
        }
        values.update(kwargs)
        return self.env["fx.revaluation"].create(values)

    def _book_rate(self, line):
        """Rate implied by the book value of one revaluation line."""
        self.assertTrue(line.amount_currency)
        self.assertTrue(line.balance_company)
        return line.balance_company / line.amount_currency

    def test_01_compute_ignores_other_currencies(self):
        self._require_accounting()
        self._open_item(self.customer, self.receivable_account, 1000.0)
        self._open_item(self.customer, self.receivable_account, 500.0,
                        currency=self.company_currency)
        revaluation = self._revaluation()
        self.assertTrue(revaluation.action_compute())
        self.assertEqual(len(revaluation.line_ids), 1)
        line = revaluation.line_ids
        self.assertAlmostEqual(line.amount_currency, 1000.0, places=2)
        self.assertEqual(line.partner_id, self.customer)
        self.assertEqual(line.currency_id, self.foreign)

    def test_02_gain_on_receivable_when_rate_rises(self):
        self._require_accounting()
        self._open_item(self.customer, self.receivable_account, 1000.0)
        revaluation = self._revaluation()
        revaluation.action_compute()
        line = revaluation.line_ids
        self.assertEqual(len(line), 1)
        revaluation.write({"rate": self._book_rate(line) * 1.1})
        self.assertGreater(line.gain_loss, 0.0)
        self.assertAlmostEqual(
            line.new_balance, line.amount_currency * revaluation.rate,
            places=2)
        self.assertAlmostEqual(
            line.gain_loss, line.balance_company * 0.1, places=2)
        self.assertAlmostEqual(revaluation.total_gain, line.gain_loss,
                               places=2)
        self.assertAlmostEqual(revaluation.total_loss, 0.0, places=2)

    def test_03_loss_on_payable_when_rate_rises(self):
        self._require_accounting()
        self._open_item(self.supplier, self.payable_account, -1200.0)
        revaluation = self._revaluation()
        revaluation.action_compute()
        line = revaluation.line_ids
        self.assertEqual(len(line), 1)
        self.assertLess(line.amount_currency, 0.0)
        self.assertLess(line.balance_company, 0.0)
        revaluation.write({"rate": self._book_rate(line) * 1.1})
        self.assertLess(line.gain_loss, 0.0)
        self.assertAlmostEqual(revaluation.total_loss, -line.gain_loss,
                               places=2)
        self.assertAlmostEqual(revaluation.net_gain_loss,
                               -revaluation.total_loss, places=2)

    def test_04_net_result_is_gain_minus_loss(self):
        self._require_accounting()
        self._open_item(self.customer, self.receivable_account, 1000.0)
        self._open_item(self.supplier, self.payable_account, -800.0)
        revaluation = self._revaluation()
        revaluation.action_compute()
        self.assertEqual(len(revaluation.line_ids), 2)
        receivable_line = revaluation.line_ids.filtered(
            lambda line: line.amount_currency > 0)
        payable_line = revaluation.line_ids.filtered(
            lambda line: line.amount_currency < 0)
        self.assertEqual(len(receivable_line), 1)
        self.assertEqual(len(payable_line), 1)
        revaluation.write({"rate": self._book_rate(receivable_line) * 1.1})
        self.assertGreater(revaluation.total_gain, 0.0)
        self.assertGreater(revaluation.total_loss, 0.0)
        self.assertAlmostEqual(
            revaluation.net_gain_loss,
            revaluation.total_gain - revaluation.total_loss, places=2)

    def test_05_post_creates_a_balanced_move(self):
        self._require_accounting()
        self._open_item(self.customer, self.receivable_account, 1000.0)
        revaluation = self._revaluation()
        revaluation.action_compute()
        line = revaluation.line_ids
        revaluation.write({"rate": self._book_rate(line) * 1.1})
        self.assertTrue(revaluation.action_post())
        self.assertEqual(revaluation.state, "posted")
        move = revaluation.move_id
        self.assertTrue(move)
        self.assertEqual(move.state, "posted")
        self.assertEqual(len(move.line_ids), 2)
        self.assertAlmostEqual(
            sum(move.line_ids.mapped("debit")),
            sum(move.line_ids.mapped("credit")), places=2)
        self.assertIn(revaluation.gain_account_id, move.line_ids.account_id)
        no_journal = self._revaluation(journal_id=False)
        no_journal.action_compute()
        with self.assertRaises(UserError):
            no_journal.action_post()

    def test_06_reset_returns_to_draft(self):
        self._require_accounting()
        self._open_item(self.customer, self.receivable_account, 600.0)
        revaluation = self._revaluation()
        revaluation.action_compute()
        with self.assertRaises(UserError):
            revaluation.action_reset()
        line = revaluation.line_ids
        revaluation.write({"rate": self._book_rate(line) * 1.5})
        revaluation.action_post()
        self.assertEqual(revaluation.state, "posted")
        with self.assertRaises(UserError):
            revaluation.action_compute()
        with self.assertRaises(UserError):
            revaluation.write({"rate": 2.0})
        self.assertTrue(revaluation.action_reset())
        self.assertEqual(revaluation.state, "draft")
        self.assertFalse(revaluation.move_id)
        self.assertTrue(revaluation.action_compute())
        self.assertEqual(len(revaluation.line_ids), 1)

    def test_07_rate_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.env["fx.revaluation"].create({
                "currency_id": self.foreign.id, "rate": 0.0})
        with self.assertRaises(ValidationError):
            self.env["fx.revaluation"].create({
                "currency_id": self.foreign.id, "rate": -2.0})
        revaluation = self.env["fx.revaluation"].create({
            "currency_id": self.foreign.id, "rate": 1.25})
        self.assertAlmostEqual(revaluation.rate, 1.25, places=4)
        with self.assertRaises(ValidationError):
            revaluation.write({"rate": 0.0})

    def test_08_default_date_is_today(self):
        revaluation = self.env["fx.revaluation"].create({
            "currency_id": self.foreign.id})
        self.assertEqual(
            revaluation.date,
            fields.Date.context_today(revaluation))
        self.assertEqual(revaluation.state, "draft")
        self.assertAlmostEqual(revaluation.rate, 1.0, places=4)
        self.assertTrue(revaluation.name.startswith("FXR/"))
        self.assertEqual(revaluation.company_id, self.company)
