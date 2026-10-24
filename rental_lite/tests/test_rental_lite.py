# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRentalLite(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Rental Customer", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "Rental Driller", "type": "service",
            "is_rental": True, "rental_price": 50.0,
            "rental_stock": 2, "rental_deposit": 200.0,
            "list_price": 50.0, "taxes_id": [(5, 0, 0)]})

    def _contract(self, start=None, end=None, quantity=1):
        start = start or date(2026, 3, 1)
        end = end or date(2026, 3, 3)
        return self.env["rental.contract"].create({
            "partner_id": self.partner.id,
            "date_start": start,
            "date_end": end,
            "deposit_amount": 200.0,
            "line_ids": [(0, 0, {
                "product_id": self.product.id,
                "quantity": quantity,
                "unit_price": 50.0,
            })],
        })

    def test_01_sequence_and_days(self):
        contract = self._contract()
        self.assertTrue(contract.name.startswith("RENT/"))
        self.assertEqual(contract.day_count, 3)
        self.assertAlmostEqual(contract.rental_total, 150.0, places=2)
        self.assertAlmostEqual(contract.total_amount, 350.0, places=2)

    def test_02_confirm(self):
        contract = self._contract()
        contract.action_confirm()
        self.assertEqual(contract.state, "confirmed")
        contract.action_pickup()
        self.assertEqual(contract.state, "picked_up")

    def test_03_availability_blocks_double_booking(self):
        first = self._contract(quantity=2)
        first.action_confirm()
        second = self._contract(quantity=1)
        with self.assertRaises(UserError):
            second.action_confirm()

    def test_04_no_overlap_allows(self):
        first = self._contract(quantity=2)
        first.action_confirm()
        second = self._contract(
            start=date(2026, 4, 1), end=date(2026, 4, 3), quantity=2)
        second.action_confirm()
        self.assertEqual(second.state, "confirmed")

    def test_05_return_and_deposit(self):
        contract = self._contract()
        contract.action_confirm()
        contract.action_pickup()
        contract.damage_fee = 40.0
        contract.return_condition = "damaged"
        contract.action_return()
        self.assertEqual(contract.state, "returned")
        self.assertTrue(contract.return_date)
        self.assertAlmostEqual(contract.deposit_refund, 160.0, places=2)

    def test_06_invoice(self):
        contract = self._contract()
        contract.action_confirm()
        contract.action_pickup()
        contract.action_return()
        contract.action_invoice()
        self.assertEqual(contract.state, "invoiced")
        self.assertTrue(contract.invoice_id)
        self.assertAlmostEqual(contract.invoice_id.amount_total, 350.0, places=2)

    def test_07_bad_dates(self):
        with self.assertRaises(Exception):
            self._contract(start=date(2026, 5, 10), end=date(2026, 5, 1))

    def test_08_overdue(self):
        contract = self._contract(
            start=date(2020, 1, 1), end=date(2020, 1, 2))
        contract.action_confirm()
        contract.action_pickup()
        contract.invalidate_recordset()
        self.assertTrue(contract.is_overdue)
