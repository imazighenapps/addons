# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockValPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.customer = cls.env.ref("stock.stock_location_customers")
        cls.other_internal = cls.env["stock.location"].create({
            "name": "StockValPro Test Overflow",
            "usage": "internal",
            "location_id": cls.stock.location_id.id,
        })
        cls.category = cls.env["product.category"].create({
            "name": "StockValPro Test Category",
        })
        cls.product_a = cls.env["product.product"].create({
            "name": "StockValPro Test Product A",
            "is_storable": True,
            "categ_id": cls.category.id,
            "standard_price": 12.0,
            "list_price": 25.0,
        })
        cls.product_b = cls.env["product.product"].create({
            "name": "StockValPro Test Product B",
            "is_storable": True,
            "categ_id": cls.category.id,
            "standard_price": 5.0,
            "list_price": 11.0,
        })

    def _move(self, qty, source, dest, product=None):
        """Create a done stock move, without relying on demo data."""
        product = product or self.product_a
        move = self.env["stock.move"].create({
            "name": "Test move",
            "product_id": product.id,
            "product_uom_qty": qty,
            "product_uom": product.uom_id.id,
            "location_id": source.id,
            "location_dest_id": dest.id,
        })
        move._action_confirm()
        move._action_assign()
        if move.move_line_ids:
            for line in move.move_line_ids:
                line.quantity = qty
        else:
            self.env["stock.move.line"].create({
                "move_id": move.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "quantity": qty,
                "location_id": source.id,
                "location_dest_id": dest.id,
            })
        move.picked = True
        move._action_done()
        # Park the move in a dedicated window so the test only sees its own
        # stock history, whatever demo data the database already contains.
        move.write({"date": datetime(2035, 1, 10, 12, 0)})
        return move

    def _report(self, **kwargs):
        values = {
            "date_from": date(2035, 1, 1),
            "date_to": date(2035, 1, 31),
        }
        values.update(kwargs)
        return self.env["stock.val.report"].create(values)

    def test_01_generate_creates_one_line_per_product(self):
        self._move(10.0, self.supplier, self.stock, product=self.product_a)
        self._move(5.0, self.supplier, self.stock, product=self.product_b)
        # An internal transfer moves stock around but does not change the
        # valuation of the company: it must not create a second line.
        self._move(3.0, self.stock, self.other_internal,
                   product=self.product_a)
        report = self._report()
        self.assertTrue(report.action_generate())
        self.assertEqual(len(report.line_ids), 2)
        line_a = report.line_ids.filtered(
            lambda line: line.product_id == self.product_a)
        line_b = report.line_ids.filtered(
            lambda line: line.product_id == self.product_b)
        self.assertEqual(len(line_a), 1)
        self.assertEqual(len(line_b), 1)
        self.assertEqual(line_a.categ_id, self.category)
        self.assertAlmostEqual(line_a.unit_cost, 12.0, places=2)
        self.assertAlmostEqual(line_a.qty_in, 10.0, places=2)
        self.assertAlmostEqual(line_a.qty_out, 0.0, places=2)
        self.assertAlmostEqual(line_b.qty_in, 5.0, places=2)
        # Generating again replaces the lines instead of duplicating them.
        report.action_generate()
        self.assertEqual(len(report.line_ids), 2)

    def test_02_inbound_and_outbound_quantities(self):
        self._move(10.0, self.supplier, self.stock, product=self.product_a)
        self._move(4.0, self.stock, self.customer, product=self.product_a)
        report = self._report(location_id=self.stock.id)
        report.action_generate()
        self.assertEqual(len(report.line_ids), 1)
        line = report.line_ids
        self.assertAlmostEqual(line.qty_in, 10.0, places=2)
        self.assertAlmostEqual(line.qty_out, 4.0, places=2)
        self.assertAlmostEqual(line.balance_qty, 6.0, places=2)

    def test_03_balance_value_uses_the_line_unit_cost(self):
        self._move(10.0, self.supplier, self.stock, product=self.product_a)
        report = self._report(location_id=self.stock.id)
        report.action_generate()
        line = report.line_ids
        self.assertAlmostEqual(line.value_in, 120.0, places=2)
        self.assertAlmostEqual(line.value_out, 0.0, places=2)
        self.assertAlmostEqual(line.balance_value, 120.0, places=2)
        # A later cost update must not rewrite a report already generated.
        self.product_a.write({"standard_price": 99.0})
        self.assertAlmostEqual(line.unit_cost, 12.0, places=2)
        self.assertAlmostEqual(line.balance_value, 120.0, places=2)
        # A new generation captures the cost of the day.
        report.action_generate()
        self.assertAlmostEqual(report.line_ids.unit_cost, 99.0, places=2)
        self.assertAlmostEqual(report.line_ids.balance_value, 990.0, places=2)

    def test_04_totals_are_the_sum_of_the_lines(self):
        self._move(10.0, self.supplier, self.stock, product=self.product_a)
        self._move(2.0, self.stock, self.customer, product=self.product_a)
        self._move(5.0, self.supplier, self.stock, product=self.product_b)
        report = self._report(location_id=self.stock.id)
        report.action_generate()
        self.assertAlmostEqual(report.total_in_qty, 15.0, places=2)
        self.assertAlmostEqual(report.total_out_qty, 2.0, places=2)
        self.assertAlmostEqual(
            report.total_value,
            sum(report.line_ids.mapped("balance_value")), places=2)
        self.assertAlmostEqual(
            report.total_value, (8.0 * 12.0) + (5.0 * 5.0), places=2)

    def test_05_empty_period_creates_no_line(self):
        self._move(10.0, self.supplier, self.stock, product=self.product_a)
        report = self._report(
            date_from=date(2001, 1, 1), date_to=date(2001, 12, 31))
        report.action_generate()
        self.assertFalse(report.line_ids)
        self.assertEqual(report.total_in_qty, 0.0)
        self.assertEqual(report.total_out_qty, 0.0)
        self.assertEqual(report.total_value, 0.0)

    def test_06_invalid_dates_are_refused(self):
        with self.assertRaises(ValidationError):
            self._report(date_from=date.today(),
                         date_to=date.today() - timedelta(days=5))
        report = self._report()
        with self.assertRaises(ValidationError):
            report.write({"date_from": report.date_to + timedelta(days=1)})

    def test_07_slow_mover_flag(self):
        self._move(10.0, self.supplier, self.stock, product=self.product_a)
        self._move(10.0, self.supplier, self.stock, product=self.product_b)
        self._move(10.0, self.stock, self.customer, product=self.product_b)
        report = self._report(location_id=self.stock.id)
        report.action_generate()
        line_a = report.line_ids.filtered(
            lambda line: line.product_id == self.product_a)
        line_b = report.line_ids.filtered(
            lambda line: line.product_id == self.product_b)
        self.assertTrue(line_a.slow_mover)
        self.assertFalse(line_b.slow_mover)
        self.assertAlmostEqual(line_a.balance_qty, 10.0, places=2)
        self.assertAlmostEqual(line_b.balance_qty, 0.0, places=2)

    def test_08_confirm_locks_the_report(self):
        self._move(10.0, self.supplier, self.stock, product=self.product_a)
        report = self._report(location_id=self.stock.id)
        report.action_generate()
        self.assertTrue(report.action_confirm())
        self.assertEqual(report.state, "confirmed")
        with self.assertRaises(UserError):
            report.action_generate()
        with self.assertRaises(UserError):
            report.write({"date_to": date.today()})
        with self.assertRaises(UserError):
            self.env["stock.val.report.line"].create({
                "report_id": report.id,
                "product_id": self.product_b.id,
                "qty_in": 1.0,
            })
        with self.assertRaises(UserError):
            report.line_ids.write({"qty_in": 20.0})
        self.assertTrue(report.action_reset())
        self.assertEqual(report.state, "draft")
        self.assertTrue(report.action_generate())
        self.assertEqual(len(report.line_ids), 1)
