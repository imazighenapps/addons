# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestExpenseGuard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.approver = cls.env["res.users"].create({
            "name": "Expense Approver",
            "login": "expense_approver_test",
            "email": "expense.approver@example.com",
            "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
        })
        cls.employee = cls.env["hr.employee"].create({
            "name": "Expense Employee",
            "user_id": cls.env.user.id,
            "expense_manager_id": cls.approver.id,
        })
        cls.product = cls.env["product.product"].create({
            "name": "Travel Expense",
            "type": "service",
            "can_be_expensed": True,
            "standard_price": 100.0,
            "list_price": 100.0,
            "taxes_id": [(5, 0, 0)],
            "supplier_taxes_id": [(5, 0, 0)],
        })
        # A demo database may already contain policies: disable them so the
        # tests only exercise the policy created below (rolled back after).
        cls.env["expense.policy"].search([]).write({"active": False})
        cls.policy = cls.env["expense.policy"].create({
            "name": "Travel cap",
            "product_id": cls.product.id,
            "max_amount": 100.0,
            "require_receipt": True,
            "max_age_days": 30,
            "block_mode": "block",
        })

    def _expense(self, amount, expense_date=None):
        return self.env["hr.expense"].create({
            "name": "Claim",
            "employee_id": self.employee.id,
            "product_id": self.product.id,
            "quantity": amount / 100.0,
            "tax_ids": [(5, 0, 0)],
            "date": expense_date or date.today(),
        })

    def _receipt(self, expense):
        attachment = self.env["ir.attachment"].create({
            "name": "receipt.txt",
            "raw": b"receipt",
            "res_model": "hr.expense",
            "res_id": expense.id,
        })
        expense.attachment_ids = [(4, attachment.id)]
        return attachment

    def test_01_compliant_expense(self):
        expense = self._expense(50.0)
        self._receipt(expense)
        expense.action_submit()
        self.assertEqual(expense.policy_state, "ok")
        approval = getattr(expense, "approval_state", False)
        if approval:
            self.assertIn(approval, ("submitted", "approved"))

    def test_02_amount_cap_blocks(self):
        expense = self._expense(150.0)
        self._receipt(expense)
        self.assertAlmostEqual(expense.total_amount_currency, 150.0, places=2)
        blocking, warnings = expense._run_expense_policy()
        self.assertTrue(blocking)
        self.assertFalse(warnings)
        self.assertEqual(expense.policy_state, "blocked")
        self.assertIn("exceeds the cap", expense.policy_note)

    def test_03_receipt_required(self):
        expense = self._expense(20.0)
        blocking, warnings = expense._run_expense_policy()
        self.assertTrue(blocking)
        self.assertEqual(expense.policy_state, "blocked")
        self.assertIn("receipt", expense.policy_note.lower())

    def test_04_max_age_blocks(self):
        expense = self._expense(
            20.0, expense_date=date.today() - timedelta(days=60))
        self._receipt(expense)
        with self.assertRaises(UserError):
            expense.action_submit()

    def test_05_warn_mode_allows(self):
        self.policy.block_mode = "warn"
        expense = self._expense(150.0)
        self._receipt(expense)
        expense.action_submit()
        self.assertEqual(expense.policy_state, "warned")
        self.assertTrue(expense.policy_note)
        self.assertTrue(expense.message_ids)

    def test_06_audit_trail(self):
        expense = self._expense(150.0)
        blocking, warnings = expense._run_expense_policy()
        self.assertTrue(blocking)
        audits = self.env["expense.audit"].search([
            ("expense_id", "=", expense.id)])
        self.assertTrue(audits)
        self.assertEqual(audits[0].level, "block")
        self.assertTrue(audits[0].name.startswith("EXP/"))

    def test_07_policy_matching(self):
        other_product = self.env["product.product"].create({
            "name": "Other Expense", "type": "service",
            "can_be_expensed": True, "standard_price": 10.0,
            "taxes_id": [(5, 0, 0)], "supplier_taxes_id": [(5, 0, 0)]})
        expense = self.env["hr.expense"].create({
            "name": "Other claim",
            "employee_id": self.employee.id,
            "product_id": other_product.id,
            "quantity": 50.0,
            "tax_ids": [(5, 0, 0)],
            "date": date.today(),
        })
        blocking, warnings = expense._run_expense_policy()
        self.assertFalse(blocking)
        self.assertEqual(expense.policy_state, "ok")
