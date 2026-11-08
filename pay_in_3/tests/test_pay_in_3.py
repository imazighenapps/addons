# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPayIn3(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "PayIn3 Test Customer", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "PayIn3 Test Service", "type": "service",
            "list_price": 100.0})

    def _invoice(self, amount=100.0, due=date(2099, 1, 10)):
        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "invoice_date": date(2099, 1, 1),
            "invoice_date_due": due,
            "invoice_line_ids": [(0, 0, {
                "product_id": self.product.id,
                "quantity": amount / 100.0,
                "price_unit": 100.0,
            })],
        })
        move.action_post()
        return move

    def _plan(self, count=3, interval=30, amount=100.0,
              first=date(2099, 1, 10)):
        move = self._invoice(amount=amount, due=first)
        return self.env["payment.plan"].create({
            "move_id": move.id,
            "total_amount": amount,
            "installment_count": count,
            "interval_days": interval,
            "first_due_date": first,
        })

    def test_01_three_installments(self):
        plan = self._plan()
        plan.action_confirm()
        self.assertEqual(len(plan.line_ids), 3)
        self.assertEqual(plan.line_ids[0].due_date, date(2099, 1, 10))
        self.assertEqual(plan.line_ids[1].due_date, date(2099, 2, 9))
        self.assertEqual(plan.line_ids[2].due_date, date(2099, 3, 11))
        self.assertEqual(plan.state, "active")

    def test_02_sum_equals_total(self):
        plan = self._plan(amount=100.0)
        plan.action_confirm()
        amounts = plan.line_ids.mapped("amount")
        self.assertAlmostEqual(sum(amounts), 100.0, places=2)
        self.assertAlmostEqual(amounts[0], 33.33, places=2)
        self.assertAlmostEqual(amounts[2], 33.34, places=2)

    def test_03_four_installments_short_interval(self):
        plan = self._plan(count=4, interval=15)
        plan.action_confirm()
        self.assertEqual(len(plan.line_ids), 4)
        self.assertEqual(plan.line_ids[1].due_date,
                         date(2099, 1, 10) + timedelta(days=15))

    def test_04_mark_paid_updates_the_plan(self):
        plan = self._plan()
        plan.action_confirm()
        first = plan.line_ids[0]
        first.action_mark_paid()
        plan.invalidate_recordset()
        self.assertEqual(first.state, "paid")
        self.assertAlmostEqual(plan.paid_amount, first.amount, places=2)
        self.assertAlmostEqual(plan.remaining_amount,
                               100.0 - first.amount, places=2)

    def test_05_register_payment_action(self):
        plan = self._plan()
        plan.action_confirm()
        action = plan.line_ids[0].action_register_payment()
        self.assertEqual(action["res_model"], "account.payment.register")
        self.assertEqual(action["context"]["active_ids"],
                         [plan.move_id.id])
        self.assertAlmostEqual(
            action["context"]["default_amount"],
            plan.line_ids[0].amount, places=2)

    def test_06_cancel_and_recompute(self):
        plan = self._plan()
        plan.action_confirm()
        self.assertTrue(plan.action_recompute())
        self.assertEqual(len(plan.line_ids), 3)
        plan.line_ids[0].action_mark_paid()
        with self.assertRaises(UserError):
            plan.action_recompute()
        self.assertTrue(plan.action_cancel())
        self.assertEqual(plan.state, "cancelled")

    def test_07_invoice_helpers(self):
        move = self._invoice()
        action = move.action_create_payment_plan()
        self.assertEqual(action["res_model"], "payment.plan")
        self.assertEqual(move.payment_plan_count, 1)
        plan = move.payment_plan_ids
        self.assertAlmostEqual(plan.total_amount, move.amount_total, places=2)
        opened = move.action_open_payment_plan()
        self.assertEqual(opened["res_id"], plan.id)

    def test_08_company_isolation(self):
        other = self.env["res.company"].create({
            "name": "PayIn3 Other Company"})
        plan = self._plan()
        plan.action_confirm()
        self.assertTrue(plan.line_ids)
        self.assertEqual(plan.company_id, self.env.company)
        self.assertNotEqual(plan.company_id, other)
