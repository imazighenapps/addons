# -*- coding: utf-8 -*-
from datetime import date, datetime

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestSalesTarget(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.customer = cls.env["res.partner"].create({
            "name": "Target customer",
        })

    def _product(self):
        return self.env["product.product"].create({"name": "Target service"})

    def _order(self, amount, day, state="sale"):
        # In Odoo 20 the confirmation stamps the order date with the
        # confirmation time, so the historical window date is written after
        # the confirm, the way an import of old orders would.
        order = self.env["sale.order"].create({
            "partner_id": self.customer.id,
            "order_line": [(0, 0, {
                "product_id": self._product().id,
                "product_uom_qty": 1.0,
                "price_unit": amount,
            })],
        })
        if state != "draft":
            order.action_confirm()
            order.write({"date_order": datetime(
                day.year, day.month, day.day, 12, 0)})
        if state == "cancel":
            # In 18.0 action_cancel() opens a cancellation wizard instead of
            # cancelling directly, so the state is written here: the test
            # only needs a cancelled order, whatever the series.
            order.write({"state": "cancel"})
        return order

    def _target(self, user=None, date_from=None, date_to=None, amount=2000.0):
        return self.env["sales.target"].create({
            "name": "Target January",
            "user_id": (user or self.env.user).id,
            "date_from": date_from or date(2099, 1, 1),
            "date_to": date_to or date(2099, 1, 31),
            "target_amount": amount,
        })

    def test_01_a_confirmed_order_is_part_of_the_target(self):
        self._order(1200.0, date(2099, 1, 10))
        target = self._target()
        self.assertAlmostEqual(
            target.achieved_amount, 1200.0, places=2)

    def test_02_draft_and_cancelled_orders_stay_out(self):
        self._order(1200.0, date(2099, 1, 10), state="draft")
        self._order(1200.0, date(2099, 1, 10), state="cancel")
        target = self._target()
        self.assertAlmostEqual(target.achieved_amount, 0.0, places=2)

    def test_03_orders_outside_the_window_stay_out(self):
        self._order(1200.0, date(1998, 1, 10))
        target = self._target()
        self.assertAlmostEqual(target.achieved_amount, 0.0, places=2)

    def test_04_an_order_of_the_other_seller_stays_out(self):
        other_seller = new_test_user(
            self.env, login="target_second_seller")
        order = self._order(1200.0, date(2099, 1, 10))
        order.write({"user_id": other_seller.id})
        target = self._target()
        self.assertAlmostEqual(target.achieved_amount, 0.0, places=2)

    def test_05_the_gap_and_the_percentage_are_consistent(self):
        self._order(400.0, date(2099, 1, 10))
        target = self._target()
        self.assertAlmostEqual(target.gap_amount, 1600.0, places=2)
        self.assertAlmostEqual(target.progress, 20.0, places=2)

    def test_06_the_target_runs_then_closes(self):
        target = self._target()
        target.action_start()
        self.assertEqual(target.state, "running")
        target.action_done()
        self.assertEqual(target.state, "done")
        with self.assertRaises(UserError):
            target.action_done()

    def test_07_the_window_is_validated(self):
        with self.assertRaises(ValidationError):
            self._target(date_to=date(2098, 12, 31))
        with self.assertRaises(ValidationError):
            self._target(amount=0.0)

    def test_08_companies_are_isolated(self):
        other = self.env["res.company"].create({"name": "Target B"})
        self._order(1200.0, date(2099, 1, 10))
        target = self.env["sales.target"].with_company(other).create({
            "name": "Target B",
            "user_id": self.env.user.id,
            "date_from": date(2099, 1, 1),
            "date_to": date(2099, 1, 31),
            "target_amount": 2000.0,
            "company_id": other.id,
        })
        target.invalidate_recordset()
        self.assertAlmostEqual(target.achieved_amount, 0.0, places=2)
