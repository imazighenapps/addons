# -*- coding: utf-8 -*-
from datetime import date, datetime

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPriceWatch(TransactionCase):
    cost_a = 100.0
    cost_b = 115.0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Everything shared by the whole class lives in setUpClass: the
        # per-test rollback deletes per-test records, so caching through
        # attributes would point at deleted rows.
        cls.vendor = cls.env["res.partner"].create({
            "name": "Vendor watch test",
        })
        cls.product = cls.env["product.product"].create({
            "name": "Watch ref B52",
        })

    def _order(self, price, day, partner=None):
        vendor = partner or self.vendor
        order = self.env["purchase.order"].create({
            "partner_id": vendor.id,
            "date_order": datetime(day.year, day.month, day.day, 10, 0),
            "order_line": [(0, 0, {
                "product_id": self.product.id,
                "product_qty": 1.0,
                "price_unit": price,
                "date_planned": datetime(day.year, day.month, day.day, 12, 0),
            })],
        })
        order.button_confirm()
        return order

    def _rule(self, threshold=5.0):
        return self.env["price.watch.rule"].create({
            "name": "Watch rule test",
            "threshold_pct": threshold,
        })

    def _scan(self):
        wizard = self.env["price.scan.wizard"].create({
            "date_from": date(2000, 1, 1),
            "date_to": date(2099, 12, 31),
        })
        wizard.action_scan()
        return wizard

    def test_01_an_order_above_the_threshold_alerts(self):
        self._rule()
        self._order(self.cost_a, date(2026, 1, 5))
        order = self._order(self.cost_b, date(2026, 3, 5))
        self._scan()
        alert = self.env["price.watch"].search([
            ("order_id", "=", order.id)])
        self.assertEqual(len(alert), 1)
        self.assertAlmostEqual(alert.previous_price, self.cost_a, places=2)
        self.assertAlmostEqual(alert.new_price, self.cost_b, places=2)
        self.assertAlmostEqual(alert.variation_pct, 15.0, places=2)

    def test_02_a_small_variation_stays_silent(self):
        self._rule(threshold=20.0)
        self._order(self.cost_a, date(2026, 1, 5), partner=self.vendor)
        self._order(self.cost_b, date(2026, 2, 5), partner=self.vendor)
        self._scan()
        self.assertFalse(self.env["price.watch"].search([]))

    def test_03_a_first_order_never_alerts(self):
        self._rule()
        order = self._order(self.cost_a, date(2026, 1, 5))
        self._scan()
        self.assertFalse(self.env["price.watch"].search([
            ("order_id", "=", order.id)]))

    def test_04_scanning_twice_never_duplicates(self):
        self._rule()
        self._order(self.cost_a, date(2026, 1, 5))
        self._order(self.cost_b, date(2026, 3, 5))
        self._scan()
        count = self.env["price.watch"].search_count([])
        self._scan()
        self.assertEqual(
            self.env["price.watch"].search_count([]), count)

    def test_05_an_alert_can_be_reviewed(self):
        self._rule()
        self._order(self.cost_a, date(2026, 1, 5))
        self._order(self.cost_b, date(2026, 3, 5))
        self._scan()
        alert = self.env["price.watch"].search([])
        alert.action_review()
        self.assertEqual(alert.state, "reviewed")

    def test_06_an_alert_can_be_ignored_and_reopened(self):
        self._rule()
        self._order(self.cost_a, date(2026, 1, 5))
        self._order(self.cost_b, date(2026, 3, 5))
        self._scan()
        alert = self.env["price.watch"].search([])
        alert.action_ignore()
        self.assertEqual(alert.state, "ignored")
        alert.action_reopen()
        self.assertEqual(alert.state, "new")

    def test_07_the_variation_is_recorded_in_percent(self):
        self._rule()
        self._order(self.cost_a, date(2026, 1, 5))
        self._order(self.cost_b, date(2026, 3, 5))
        self._scan()
        alert = self.env["price.watch"].search([])
        self.assertAlmostEqual(alert.variation_pct, 15.0, places=2)

    def test_08_companies_are_isolated(self):
        other = self.env["res.company"].create({"name": "Watch B"})
        self.env["price.watch.rule"].with_company(other).create({
            "name": "Watch B rule",
            "threshold_pct": 1.0,
            "company_id": other.id,
        })
        self._order(self.cost_a, date(2026, 1, 5))
        self._order(self.cost_b, date(2026, 3, 5))
        wizard = self.env["price.scan.wizard"].with_company(other).create({
            "date_from": date(2000, 1, 1),
            "date_to": date(2099, 12, 31),
            "rule_ids": [(6, 0, self.env["price.watch.rule"].search(
                [("company_id", "=", other.id)]).ids)],
        })
        wizard.action_scan()
        self.assertFalse(self.env["price.watch"].with_company(
            other).search([]))
