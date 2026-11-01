# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMatchControlPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "MatchControl Test Vendor", "is_company": True,
            "supplier_rank": 1})
        cls.product = cls.env["product.product"].create({
            "name": "MatchControl Test Product", "type": "consu",
            "is_storable": True, "standard_price": 100.0,
            "list_price": 120.0})
        cls.journal = cls.env["account.journal"].search([
            ("type", "=", "purchase"),
            ("company_id", "=", cls.env.company.id)], limit=1)
        if not cls.journal:
            cls.journal = cls.env["account.journal"].create({
                "name": "MatchControl Purchases", "code": "MTCPUR",
                "type": "purchase"})
        cls.expense = cls.env["account.account"].search([
            ("account_type", "=", "expense"),
            ("company_ids", "in", cls.env.company.id)], limit=1)

    def _order(self, qty, price=100.0):
        order = self.env["purchase.order"].create({
            "partner_id": self.partner.id,
            "order_line": [(0, 0, {
                "product_id": self.product.id,
                "name": "MatchControl order line",
                "product_qty": qty,
                "price_unit": price,
            })],
        })
        order.button_confirm()
        return order

    def _receive(self, order, qty):
        picking = order.picking_ids[:1]
        self.assertTrue(picking, "The confirmed order should have a receipt.")
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity = qty
            move.picked = True
        picking.with_context(
            skip_backorder=True, skip_sms=True).button_validate()
        self.assertEqual(picking.state, "done")
        return picking

    def _bill(self, qty, price=100.0, order=None):
        line = {
            "product_id": self.product.id,
            "name": "MatchControl vendor line",
            "quantity": qty,
            "price_unit": price,
            "tax_ids": [(5, 0, 0)],
        }
        if self.expense:
            line["account_id"] = self.expense.id
        bill = self.env["account.move"].create({
            "move_type": "in_invoice",
            "partner_id": self.partner.id,
            "journal_id": self.journal.id,
            "invoice_date": date(2026, 6, 1),
            "invoice_origin": order.name if order else False,
            "invoice_line_ids": [(0, 0, line)],
        })
        bill.action_post()
        return bill

    def _check(self, order, picking, bill, tolerance=2.0):
        return self.env["match.check"].create({
            "partner_id": self.partner.id,
            "purchase_id": order.id,
            "picking_id": picking.id,
            "bill_id": bill.id,
            "date": date(2026, 6, 1),
            "tolerance_pct": tolerance,
        })

    def _scenario(self, qty=10.0, price=100.0, bill_qty=None,
                  bill_price=None, tolerance=2.0):
        bill_qty = qty if bill_qty is None else bill_qty
        bill_price = price if bill_price is None else bill_price
        order = self._order(qty, price)
        picking = self._receive(order, qty)
        bill = self._bill(bill_qty, bill_price, order)
        return self._check(order, picking, bill, tolerance)

    def test_01_quantity_variance_is_an_exception(self):
        check = self._scenario(qty=10.0, bill_qty=12.0)
        self.assertTrue(check.action_run())
        self.assertEqual(check.state, "exception")
        self.assertEqual(len(check.line_ids), 1)
        self.assertEqual(check.line_ids.status, "qty")
        self.assertAlmostEqual(check.total_received, 1000.0, places=2)
        self.assertAlmostEqual(check.total_billed, 1200.0, places=2)

    def test_02_variance_within_tolerance_is_ok(self):
        check = self._scenario(qty=10.0, bill_qty=10.3, tolerance=5.0)
        check.action_run()
        self.assertEqual(check.line_ids.status, "ok")
        self.assertEqual(check.state, "ok")
        self.assertTrue(check.action_validate())
        self.assertEqual(check.state, "validated")

    def test_03_price_variance_is_detected(self):
        check = self._scenario(qty=10.0, bill_price=110.0)
        check.action_run()
        self.assertEqual(check.line_ids.status, "price")
        self.assertEqual(check.state, "exception")
        self.assertAlmostEqual(check.total_ordered, 1000.0, places=2)
        self.assertAlmostEqual(check.total_billed, 1100.0, places=2)
        self.assertAlmostEqual(check.variance_amount, 100.0, places=2)

    def test_04_validate_requires_a_reason_on_exception(self):
        check = self._scenario(qty=10.0, bill_qty=12.0)
        with self.assertRaises(UserError):
            check.action_flag_exception()
        check.action_run()
        self.assertEqual(check.state, "exception")
        with self.assertRaises(UserError):
            check.action_validate()
        self.assertEqual(check.state, "exception")
        self.assertFalse(check.exception_reason)

    def test_05_validate_with_a_reason(self):
        check = self._scenario(qty=10.0, bill_qty=12.0)
        check.action_run()
        self.assertTrue(check.action_flag_exception(
            "Over-delivery accepted by the buyer."))
        self.assertEqual(check.state, "exception")
        self.assertTrue(check.action_validate())
        self.assertEqual(check.state, "validated")
        with self.assertRaises(UserError):
            check.action_run()

    def test_06_totals_are_computed_from_the_lines(self):
        check = self._scenario(qty=10.0, price=100.0)
        check.action_run()
        self.assertAlmostEqual(check.total_ordered, 1000.0, places=2)
        self.assertAlmostEqual(check.total_received, 1000.0, places=2)
        self.assertAlmostEqual(check.total_billed, 1000.0, places=2)
        self.assertAlmostEqual(check.variance_amount, 0.0, places=2)
        self.assertEqual(check.state, "ok")

        order = self._order(4.0, 150.0)
        picking = self._receive(order, 4.0)
        bill = self._bill(4.0, 175.0, order)
        second = self._check(order, picking, bill)
        second.action_run()
        self.assertAlmostEqual(second.total_ordered, 600.0, places=2)
        self.assertAlmostEqual(second.total_billed, 700.0, places=2)
        self.assertAlmostEqual(second.variance_amount, 100.0, places=2)

    def test_07_duplicate_bill_is_refused(self):
        check = self._scenario(qty=10.0)
        check.action_run()
        with self.assertRaises(UserError):
            self._check(check.purchase_id, check.picking_id, check.bill_id)
        self.assertEqual(check.state, "ok")

    def test_08_reset_returns_to_draft(self):
        check = self._scenario(qty=10.0, bill_qty=12.0)
        check.action_run()
        check.write({"exception_reason": "Waiting for the credit note."})
        check.action_validate()
        self.assertEqual(check.state, "validated")
        self.assertTrue(check.action_reset())
        self.assertEqual(check.state, "draft")
        self.assertFalse(check.exception_reason)
        self.assertTrue(check.line_ids)
