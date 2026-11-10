# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEarlyPayDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "EarlyPay Other Company"})
        cls.vendor = cls.env["res.partner"].create({
            "name": "EarlyPay Vendor"})
        cls.offer = cls.env["earlypay.offer"].create({
            "name": "BILL-2026-1101",
            "partner_id": cls.vendor.id,
            "gross_amount": 1000.0,
            "discount_rate": 2.0,
            "invoice_date": date(2026, 11, 1),
            "discount_deadline": date(2026, 11, 10),
            "due_date": date(2026, 11, 30),
        })

    def test_01_offer_defaults(self):
        self.assertEqual(self.offer.state, "open")
        self.assertEqual(self.offer.company_id, self.env.company)
        self.assertTrue(self.offer.is_open)
        self.assertFalse(self.offer.decided_on)

    def test_02_amounts_are_computed(self):
        self.assertAlmostEqual(self.offer.discount_amount, 20.0, places=2)
        self.assertAlmostEqual(self.offer.net_amount, 980.0, places=2)
        self.offer.write({"gross_amount": 2500.0, "discount_rate": 1.5})
        self.assertAlmostEqual(self.offer.discount_amount, 37.5, places=2)
        self.assertAlmostEqual(self.offer.net_amount, 2462.5, places=2)

    def test_03_capture_offer(self):
        self.assertTrue(self.offer.action_capture())
        self.assertEqual(self.offer.state, "captured")
        self.assertFalse(self.offer.is_open)
        self.assertTrue(self.offer.decided_on)

    def test_04_miss_and_reopen_offer(self):
        self.offer.action_miss()
        self.assertEqual(self.offer.state, "missed")
        self.assertTrue(self.offer.decided_on)
        self.offer.action_reopen()
        self.assertEqual(self.offer.state, "open")
        self.assertFalse(self.offer.decided_on)
        self.assertTrue(self.offer.is_open)

    def test_05_invalid_transitions(self):
        self.offer.action_capture()
        with self.assertRaises(UserError):
            self.offer.action_capture()
        with self.assertRaises(UserError):
            self.offer.action_miss()
        open_offer = self.env["earlypay.offer"].create({
            "name": "BILL-2026-1102",
            "partner_id": self.vendor.id,
            "gross_amount": 500.0,
            "discount_rate": 3.0,
            "invoice_date": date(2026, 12, 1),
            "discount_deadline": date(2026, 12, 10),
            "due_date": date(2026, 12, 31),
        })
        with self.assertRaises(UserError):
            open_offer.action_reopen()

    def test_06_amount_and_rate_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["earlypay.offer"].create({
                "name": "BILL-BAD-AMOUNT",
                "partner_id": self.vendor.id,
                "gross_amount": 0.0,
                "discount_rate": 2.0,
                "invoice_date": date(2026, 11, 1),
                "discount_deadline": date(2026, 11, 10),
                "due_date": date(2026, 11, 30),
            })
        with self.assertRaises(ValidationError):
            self.env["earlypay.offer"].create({
                "name": "BILL-BAD-RATE",
                "partner_id": self.vendor.id,
                "gross_amount": 100.0,
                "discount_rate": 100.0,
                "invoice_date": date(2026, 11, 1),
                "discount_deadline": date(2026, 11, 10),
                "due_date": date(2026, 11, 30),
            })

    def test_07_date_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["earlypay.offer"].create({
                "name": "BILL-BAD-DEADLINE",
                "partner_id": self.vendor.id,
                "gross_amount": 100.0,
                "discount_rate": 2.0,
                "invoice_date": date(2026, 11, 15),
                "discount_deadline": date(2026, 11, 10),
                "due_date": date(2026, 11, 30),
            })
        with self.assertRaises(ValidationError):
            self.env["earlypay.offer"].create({
                "name": "BILL-BAD-DUE",
                "partner_id": self.vendor.id,
                "gross_amount": 100.0,
                "discount_rate": 2.0,
                "invoice_date": date(2026, 11, 1),
                "discount_deadline": date(2026, 11, 20),
                "due_date": date(2026, 11, 15),
            })

    def test_08_company_isolation(self):
        foreign_vendor = self.env["res.partner"].with_company(
            self.other_company).create({"name": "EarlyPay Foreign Vendor"})
        foreign = self.env["earlypay.offer"].with_company(
            self.other_company).create({
            "name": "BILL-FOREIGN-2026",
            "partner_id": foreign_vendor.id,
            "gross_amount": 800.0,
            "discount_rate": 2.5,
            "invoice_date": date(2026, 10, 1),
            "discount_deadline": date(2026, 10, 8),
            "due_date": date(2026, 10, 31),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(self.offer.company_id, self.env.company)
        self.assertAlmostEqual(foreign.discount_amount, 20.0, places=2)
