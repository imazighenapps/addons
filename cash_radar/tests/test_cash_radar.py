# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCashRadar(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Cash Radar Customer", "is_company": True})
        cls.supplier = cls.env["res.partner"].create({
            "name": "Cash Radar Supplier", "is_company": True,
            "supplier_rank": 1})
        cls.product = cls.env["product.product"].create({
            "name": "Cash Radar Service", "type": "service",
            "list_price": 100.0})

    def _invoice(self, due, amount=1000.0, move_type="out_invoice",
                 partner=None, post=True):
        move = self.env["account.move"].create({
            "move_type": move_type,
            "partner_id": (partner or self.partner).id,
            "invoice_date": date(2099, 1, 1),
            "invoice_date_due": due,
            "invoice_line_ids": [(0, 0, {
                "product_id": self.product.id,
                "quantity": amount / 100.0,
                "price_unit": 100.0,
                "tax_ids": [(5, 0, 0)],
            })],
        })
        if post:
            move.action_post()
        return move

    def _forecast(self, weeks=13, delay=0, opening=0.0,
                  start=date(2099, 1, 1)):
        return self.env["cash.forecast"].create({
            "name": "Cash Radar Test",
            "date_from": start,
            "weeks": weeks,
            "delay_days": delay,
            "opening_balance": opening,
        })

    def _lines(self, forecast, source=None):
        lines = forecast.line_ids
        if source:
            lines = lines.filtered(lambda l: l.source == source)
        return lines

    def test_01_invoice_lands_in_its_week(self):
        forecast = self._forecast()
        self._invoice(date(2099, 3, 4))
        forecast.action_compute()
        lines = self._lines(forecast, "invoice")
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines.week_start, date(2099, 3, 2))
        self.assertEqual(lines.direction, "in")

    def test_02_vendor_bill_is_an_outflow(self):
        forecast = self._forecast()
        self._invoice(date(2099, 2, 10), move_type="in_invoice",
                      partner=self.supplier)
        forecast.action_compute()
        lines = self._lines(forecast, "bill")
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines.direction, "out")

    def test_03_draft_invoice_is_excluded(self):
        forecast = self._forecast()
        self._invoice(date(2099, 2, 10), post=False)
        forecast.action_compute()
        self.assertFalse(self._lines(forecast))

    def test_04_delay_shifts_the_invoice(self):
        forecast = self._forecast(delay=10)
        self._invoice(date(2099, 3, 4))
        forecast.action_compute()
        line = self._lines(forecast, "invoice")
        self.assertEqual(line.week_start, date(2099, 3, 9))

    def test_05_monthly_recurrence(self):
        forecast = self._forecast(start=date(2099, 1, 1))
        self.env["cash.forecast.recurrence"].create({
            "name": "Rent", "amount": -500.0, "frequency": "monthly",
            "date_start": date(2099, 1, 15),
            "date_end": date(2099, 3, 31),
        })
        forecast.action_compute()
        lines = self._lines(forecast, "recurrence")
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0].direction, "out")
        self.assertAlmostEqual(lines[0].amount, 500.0, places=2)

    def test_06_minimum_balance_is_negative(self):
        forecast = self._forecast(opening=100.0)
        self._invoice(date(2099, 2, 10), amount=800.0,
                      move_type="in_invoice", partner=self.supplier)
        forecast.action_compute()
        forecast.invalidate_recordset()
        self.assertAlmostEqual(forecast.min_balance, -700.0, places=2)
        self.assertTrue(forecast.is_at_risk)
        self.assertEqual(forecast.min_week, "2099-W07")

    def test_07_reset_clears_the_lines(self):
        forecast = self._forecast()
        self._invoice(date(2099, 2, 10))
        forecast.action_compute()
        self.assertTrue(forecast.line_ids)
        self.assertTrue(forecast.action_reset())
        self.assertFalse(forecast.line_ids)
        self.assertEqual(forecast.state, "draft")

    def test_08_company_isolation(self):
        other = self.env["res.company"].create({
            "name": "Cash Radar Other Company"})
        forecast = self._forecast()
        self._invoice(date(2099, 2, 10))
        forecast.action_compute()
        self.assertTrue(forecast.line_ids)
        self.assertEqual(forecast.line_ids.company_id, self.env.company)
        self.assertNotEqual(forecast.company_id, other)
