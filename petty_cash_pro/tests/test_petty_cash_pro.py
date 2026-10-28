# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPettyCashPro(TransactionCase):
    _fund_counter = 0

    def _fund(self, float_amount=1000.0):
        type(self)._fund_counter += 1
        counter = type(self)._fund_counter
        return self.env["petty.cash.fund"].create({
            "name": "Test Fund %s" % counter,
            "code": "PC-T%s" % counter,
            "float_amount": float_amount,
        })

    def _transaction(self, fund, txn_type="expense", amount=100.0,
                     name=None):
        return self.env["petty.cash.transaction"].create({
            "fund_id": fund.id,
            "type": txn_type,
            "name": name or "Test %s" % txn_type,
            "amount": amount,
        })

    def _reconciliation(self, fund, counted, close_fund=False):
        return self.env["petty.cash.reconciliation"].create({
            "fund_id": fund.id,
            "counted_cash": counted,
            "close_fund": close_fund,
        })

    def test_01_balance_after_topup(self):
        fund = self._fund(1000.0)
        self.assertAlmostEqual(fund.balance, 1000.0, places=2)
        topup = self._transaction(fund, "top_up", 500.0)
        topup.action_confirm()
        fund.invalidate_recordset()
        self.assertAlmostEqual(fund.balance, 1500.0, places=2)
        self.assertAlmostEqual(fund.total_topups, 500.0, places=2)
        self.assertEqual(fund.transaction_count, 1)

    def test_02_balance_after_expense_and_return(self):
        fund = self._fund(1000.0)
        expense = self._transaction(fund, "expense", 200.0)
        expense.action_confirm()
        returned = self._transaction(fund, "return", 50.0)
        returned.action_confirm()
        self._transaction(fund, "expense", 100.0)
        fund.invalidate_recordset()
        self.assertAlmostEqual(fund.balance, 850.0, places=2)
        self.assertAlmostEqual(fund.total_expenses, 200.0, places=2)
        self.assertEqual(fund.transaction_count, 3)

    def test_03_confirm_cancel_reset(self):
        fund = self._fund()
        transaction = self._transaction(fund, "expense", 120.0)
        self.assertEqual(transaction.state, "draft")
        transaction.action_confirm()
        self.assertEqual(transaction.state, "confirmed")
        self.assertEqual(transaction.confirmed_by, self.env.user)
        self.assertTrue(transaction.confirmed_date)
        transaction.action_cancel()
        self.assertEqual(transaction.state, "cancelled")
        transaction.action_reset()
        self.assertEqual(transaction.state, "draft")
        self.assertFalse(transaction.confirmed_by)
        self.assertFalse(transaction.confirmed_date)

    def test_04_closed_fund_blocks_transactions(self):
        fund = self._fund(1000.0)
        draft = self._transaction(fund, "expense", 100.0)
        reconciliation = self._reconciliation(fund, 1000.0)
        reconciliation.action_validate()
        fund.action_close()
        self.assertEqual(fund.state, "closed")
        self.assertTrue(fund.closed_date)
        with self.assertRaises(UserError):
            self._transaction(fund, "expense", 10.0)
        with self.assertRaises(UserError):
            draft.action_confirm()
        fund.action_reopen()
        self.assertEqual(fund.state, "open")
        self.assertFalse(fund.closed_date)
        draft.invalidate_recordset()
        draft.action_confirm()
        self.assertEqual(draft.state, "confirmed")

    def test_05_reconciliation_difference(self):
        fund = self._fund(1000.0)
        topup = self._transaction(fund, "top_up", 250.0)
        topup.action_confirm()
        fund.invalidate_recordset()
        reconciliation = self._reconciliation(fund, 1200.0)
        self.assertAlmostEqual(
            reconciliation.theoretical_balance, 1250.0, places=2)
        self.assertAlmostEqual(reconciliation.difference, -50.0, places=2)
        self.assertEqual(reconciliation.state, "draft")

    def test_06_close_with_gap_requires_note(self):
        fund = self._fund(1000.0)
        reconciliation = self._reconciliation(fund, 950.0)
        reconciliation.action_validate()
        self.assertEqual(reconciliation.state, "validated")
        with self.assertRaises(UserError):
            fund.action_close()
        self.assertEqual(fund.state, "open")
        reconciliation.note = "Missing receipt, charged to the fund manager."
        fund.action_close()
        self.assertEqual(fund.state, "closed")

    def test_07_close_with_zero_difference(self):
        fund = self._fund(800.0)
        reconciliation = self._reconciliation(fund, 800.0)
        reconciliation.action_validate()
        fund.action_close()
        self.assertEqual(fund.state, "closed")
        other = self._fund(500.0)
        with self.assertRaises(UserError):
            other.action_close()

    def test_08_validate_and_close_flag(self):
        fund = self._fund(500.0)
        reconciliation = self._reconciliation(fund, 500.0, close_fund=True)
        reconciliation.action_validate()
        self.assertEqual(reconciliation.state, "validated")
        self.assertEqual(fund.state, "closed")
        other = self._fund(500.0)
        gap = self._reconciliation(other, 450.0, close_fund=True)
        with self.assertRaises(UserError):
            gap.action_validate()
        self.assertEqual(gap.state, "draft")
        self.assertEqual(other.state, "open")
