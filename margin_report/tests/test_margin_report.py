# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMarginBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "MarginBook Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "MarginBook Test Customer"})

    def _book(self, **values):
        defaults = {
            "name": "MarginBook Test Order SO-26-014",
            "order_ref": "SO-26-014",
            "partner_id": self.partner.id,
            "date": date(2026, 7, 6),
            "target_rate": 25.0,
        }
        defaults.update(values)
        return self.env["margin.book"].create(defaults)

    def _line(self, book, sell=1200.0, cost=900.0, qty=1.0, **values):
        defaults = {
            "book_id": book.id,
            "description": "MarginBook Test Line",
            "quantity": qty,
            "sell_price": sell,
            "unit_cost": cost,
        }
        defaults.update(values)
        return self.env["margin.book.line"].create(defaults)

    def _filled(self, **values):
        book = self._book(**values)
        self._line(book)
        self._line(book, sell=200.0, cost=150.0)
        return book

    def test_01_sheet_defaults(self):
        book = self._book()
        self.assertEqual(book.state, "draft")
        self.assertEqual(book.company_id, self.env.company)
        self.assertEqual(book.target_rate, 25.0)
        self.assertEqual(book.line_count, 0)
        self.assertAlmostEqual(book.total_revenue, 0.0, places=2)
        self.assertAlmostEqual(book.total_cost, 0.0, places=2)
        self.assertAlmostEqual(book.margin_rate, 0.0, places=2)
        self.assertFalse(book.is_below_target)
        self.assertFalse(book.confirmed_on)

    def test_02_totals_are_computed_from_lines(self):
        book = self._filled()
        self.assertAlmostEqual(book.total_revenue, 1400.0, places=2)
        self.assertAlmostEqual(book.total_cost, 1050.0, places=2)
        self.assertAlmostEqual(book.total_margin, 350.0, places=2)
        self.assertAlmostEqual(book.margin_rate, 25.0, places=2)
        self.assertEqual(book.line_count, 2)

    def test_03_empty_revenue_never_divides(self):
        book = self._book()
        self._line(book, sell=0.0, cost=50.0)
        self.assertAlmostEqual(book.total_revenue, 0.0, places=2)
        self.assertAlmostEqual(book.margin_rate, 0.0, places=2)
        self.assertFalse(book.is_below_target)
        line = book.line_ids[0]
        self.assertAlmostEqual(line.line_margin, -50.0, places=2)
        self.assertAlmostEqual(line.line_rate, 0.0, places=2)

    def test_04_under_target_flag_moves_with_the_target(self):
        book = self._filled()
        self.assertFalse(book.is_below_target)
        book.write({"target_rate": 40.0})
        self.assertTrue(book.is_below_target)

    def test_05_confirm_freezes_the_sheet(self):
        empty = self._book(order_ref="SO-26-014E",
                           name="MarginBook Test Empty SO-26-014E")
        with self.assertRaises(UserError):
            empty.action_confirm()
        book = self._filled(order_ref="SO-26-015",
                            name="MarginBook Test Order SO-26-015")
        self.assertTrue(book.action_confirm())
        self.assertEqual(book.state, "confirmed")
        self.assertTrue(book.confirmed_on)
        with self.assertRaises(UserError):
            book.action_confirm()

    def test_06_confirmed_lines_are_locked(self):
        book = self._filled()
        line = book.line_ids[0]
        book.action_confirm()
        with self.assertRaises(UserError):
            self._line(book, sell=500.0)
        with self.assertRaises(UserError):
            line.write({"sell_price": 1500.0})
        self.assertAlmostEqual(line.sell_price, 1200.0, places=2)

    def test_07_reopen_and_reset_rules(self):
        draft = self._filled()
        with self.assertRaises(UserError):
            draft.action_reset()
        draft.action_confirm()
        self.assertTrue(draft.action_reset())
        self.assertEqual(draft.state, "draft")
        line = draft.line_ids[0]
        line.write({"sell_price": 1300.0})
        draft.action_confirm()
        self.assertEqual(draft.state, "confirmed")

    def test_08_constraints(self):
        book = self._book()
        with self.assertRaises(ValidationError):
            self._line(book, sell=-10.0)
        with self.assertRaises(ValidationError):
            self._line(book, cost=-10.0)
        with self.assertRaises(ValidationError):
            self._line(book, qty=0.0)
        with self.assertRaises(ValidationError):
            self._book(order_ref="SO-26-014",
                       name="MarginBook Test Duplicate")
        with self.assertRaises(ValidationError):
            book.write({"target_rate": 120.0})

    def test_09_search_filters_and_counters(self):
        under = self._filled(target_rate=40.0,
                             order_ref="SO-26-099",
                             name="MarginBook Test Under Target")
        healthy = self._filled()
        empty = self._book(name="MarginBook Test No Lines",
                           order_ref="SO-26-101")
        books = self.env["margin.book"]
        self.assertIn(under, books.search(
            [("is_below_target", "=", True)]))
        self.assertNotIn(healthy, books.search(
            [("is_below_target", "=", True)]))
        self.assertIn(under, books.search([("line_count", ">", 0)]))
        self.assertIn(healthy, books.search([("line_count", ">", 0)]))
        self.assertIn(empty, books.search([("line_count", "=", 0)]))
        self.assertNotIn(under, books.search([("line_count", "=", 0)]))

    def test_10_company_isolation(self):
        foreign = self.env["margin.book"].with_company(
            self.other_company).sudo().create({
            "name": "MarginBook Test Foreign Sheet",
            "order_ref": "SO-FOR-001",
            "date": date(2026, 7, 6),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._filled()
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
