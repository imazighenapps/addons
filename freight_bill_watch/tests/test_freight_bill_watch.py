# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFreightWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "FreightWatch Other Company"})
        cls.currency = cls.env.company.currency_id
        cls.tariff = cls.env["freight.tariff"].create({
            "name": "FW-TAR-2026-01",
            "carrier_name": "FreightWatch Carrier A",
            "lane": "Paris-Lyon",
            "agreed_amount": 100.0,
            "currency_id": cls.currency.id,
        })

    def _line(self, **values):
        defaults = {
            "name": "FW-BILL-2026-001",
            "tariff_id": self.tariff.id,
            "billed_amount": 120.0,
            "currency_id": self.currency.id,
            "bill_date": date(2026, 5, 12),
        }
        defaults.update(values)
        return self.env["freight.bill.line"].create(defaults)

    def test_01_tariff_and_line_defaults(self):
        line = self._line()
        self.assertEqual(self.tariff.company_id, self.env.company)
        self.assertEqual(line.state, "draft")
        self.assertEqual(line.company_id, self.env.company)
        self.assertFalse(line.disputed)

    def test_02_overcharge_computed(self):
        line = self._line(billed_amount=130.0)
        self.assertEqual(line.overcharge_amount, 30.0)
        self.assertTrue(line.is_overcharged)

    def test_03_no_overcharge_when_within_tariff(self):
        line = self._line(billed_amount=90.0)
        self.assertEqual(line.overcharge_amount, 0.0)
        self.assertFalse(line.is_overcharged)

    def test_04_check_and_dispute_workflow(self):
        line = self._line(billed_amount=150.0)
        self.assertTrue(line.action_check())
        self.assertEqual(line.state, "checked")
        self.assertTrue(line.action_dispute())
        self.assertEqual(line.state, "disputed")
        self.assertTrue(line.disputed)

    def test_05_dispute_requires_overcharge(self):
        line = self._line(billed_amount=80.0)
        with self.assertRaises(ValidationError):
            line.action_dispute()

    def test_06_negative_amounts_refused(self):
        with self.assertRaises(ValidationError):
            self.env["freight.tariff"].create({
                "name": "FW-TAR-BAD",
                "carrier_name": "FreightWatch Carrier B",
                "lane": "Lille-Nice",
                "agreed_amount": -1.0,
                "currency_id": self.currency.id,
            })
        with self.assertRaises(ValidationError):
            self._line(billed_amount=-5.0)

    def test_07_tariff_line_count(self):
        self._line(name="FW-BILL-2026-002")
        self._line(name="FW-BILL-2026-003", billed_amount=95.0)
        self.tariff.invalidate_recordset()
        self.assertEqual(self.tariff.line_count, 2)

    def test_08_overcharge_filter(self):
        over = self._line(name="FW-BILL-2026-004", billed_amount=140.0)
        ok = self._line(name="FW-BILL-2026-005", billed_amount=90.0)
        found = self.env["freight.bill.line"].search([
            ("is_overcharged", "=", True)])
        self.assertIn(over, found)
        self.assertNotIn(ok, found)

    def test_09_company_isolation(self):
        foreign_tariff = self.env["freight.tariff"].with_company(
            self.other_company).sudo().create({
            "name": "FW-TAR-F-2027",
            "carrier_name": "FreightWatch Foreign Carrier",
            "lane": "Berlin-Hamburg",
            "agreed_amount": 200.0,
            "currency_id": self.other_company.currency_id.id,
            "company_id": self.other_company.id,
        })
        foreign_line = self.env["freight.bill.line"].with_company(
            self.other_company).sudo().create({
            "name": "FW-BILL-F-2027",
            "tariff_id": foreign_tariff.id,
            "billed_amount": 220.0,
            "currency_id": self.other_company.currency_id.id,
            "bill_date": date(2027, 1, 15),
            "company_id": self.other_company.id,
        })
        local = self._line(name="FW-BILL-L-2027")
        self.assertEqual(foreign_line.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign_line.company_id, local.company_id)
