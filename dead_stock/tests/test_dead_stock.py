# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDeadStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1)
        cls.stock_location = warehouse.lot_stock_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

    def _product(self, code, price=10.0, qty=10.0):
        product = self.env["product.product"].create({
            "name": "Dead Stock %s" % code, "default_code": code,
            "type": "consu", "is_storable": True, "standard_price": price,
        })
        if qty:
            self.env["stock.quant"]._update_available_quantity(
                product, self.stock_location, qty)
        return product

    def _delivery(self, product, when):
        move = self.env["stock.move"].create({
            "name": "Test move",
            "product_id": product.id,
            "product_uom_qty": 1.0,
            "product_uom": product.uom_id.id,
            "location_id": self.stock_location.id,
            "location_dest_id": self.customer_location.id,
            "date": when,
        })
        move.write({"state": "done"})
        return move

    def _rule(self, **kwargs):
        values = {
            "name": "Dead Stock Rule",
            "slow_days": 90,
            "carrying_rate": 20.0,
            "min_value": 0.0,
        }
        values.update(kwargs)
        return self.env["dead.stock.rule"].create(values)

    def _scan(self, rule):
        scan = self.env["dead.stock.scan"].create({
            "date_ref": date(2099, 6, 30),
            "rule_id": rule.id,
        })
        scan.action_run()
        return scan

    def test_01_dormant_product_is_detected(self):
        product = self._product("DS-01")
        scan = self._scan(self._rule())
        self.assertIn(product, scan.line_ids.mapped("product_id"))
        line = scan.line_ids.filtered(lambda l: l.product_id == product)
        self.assertGreaterEqual(line.days_idle, 90)

    def test_02_recent_delivery_is_not_dormant(self):
        product = self._product("DS-02")
        self._delivery(product, "2099-06-01 10:00:00")
        scan = self._scan(self._rule())
        self.assertNotIn(product, scan.line_ids.mapped("product_id"))

    def test_03_minimum_value_filters_small_stock(self):
        self._product("DS-03", price=1.0, qty=2.0)
        scan = self._scan(self._rule(min_value=100.0))
        self.assertFalse(scan.line_ids.filtered(
            lambda l: l.product_id.default_code == "DS-03"))

    def test_04_idle_period_is_respected(self):
        recent = self._product("DS-04A")
        self._delivery(recent, "2099-06-01 10:00:00")
        old = self._product("DS-04B")
        self._delivery(old, "2099-01-01 10:00:00")
        strict = self._scan(self._rule(name="Strict", slow_days=10))
        self.assertIn(recent, strict.line_ids.mapped("product_id"))
        self.assertIn(old, strict.line_ids.mapped("product_id"))
        relaxed = self._scan(self._rule(name="Relaxed", slow_days=90))
        self.assertNotIn(recent, relaxed.line_ids.mapped("product_id"))
        self.assertIn(old, relaxed.line_ids.mapped("product_id"))

    def test_05_holding_cost(self):
        product = self._product("DS-05", price=100.0, qty=10.0)
        scan = self._scan(self._rule(carrying_rate=20.0))
        line = scan.line_ids.filtered(lambda l: l.product_id == product)
        self.assertAlmostEqual(line.value, 1000.0, places=2)
        expected = 1000.0 * 0.2 * line.days_idle / 365.0
        self.assertAlmostEqual(line.carrying_cost, expected, places=2)

    def test_06_actioned_ignored_reopen(self):
        product = self._product("DS-06")
        scan = self._scan(self._rule())
        line = scan.line_ids.filtered(lambda l: l.product_id == product)
        self.assertTrue(line.action_actioned())
        self.assertEqual(line.state, "actioned")
        self.assertTrue(line.action_ignore())
        self.assertEqual(line.state, "ignored")
        self.assertTrue(line.action_reopen())
        self.assertEqual(line.state, "open")

    def test_07_scan_totals(self):
        product = self._product("DS-07", price=50.0, qty=4.0)
        scan = self._scan(self._rule())
        line = scan.line_ids.filtered(lambda l: l.product_id == product)
        self.assertAlmostEqual(scan.total_value, sum(
            scan.line_ids.mapped("value")), places=2)
        self.assertAlmostEqual(scan.total_carrying, sum(
            scan.line_ids.mapped("carrying_cost")), places=2)
        self.assertIn(line, scan.line_ids)
        self.assertEqual(scan.product_count, len(scan.line_ids))

    def test_08_company_isolation(self):
        other = self.env["res.company"].create({
            "name": "Dead Stock Other Company"})
        self._product("DS-08")
        scan = self._scan(self._rule())
        self.assertTrue(scan.line_ids)
        self.assertEqual(scan.line_ids.company_id, self.env.company)
        self.assertNotEqual(scan.company_id, other)
