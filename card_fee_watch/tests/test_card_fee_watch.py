# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFeeWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "FeeWatch Other Company"})
        cls.currency = cls.env.company.currency_id
        cls.contract = cls.env["fee.contract"].create({
            "name": "FeeWatch Stripe FR",
            "provider": "Stripe",
            "rate_percent": 1.4,
            "fixed_fee": 0.25,
            "currency_id": cls.currency.id,
        })

    def _line(self, contract=None, **values):
        defaults = {
            "contract_id": (contract or self.contract).id,
            "billed_on": date(2026, 2, 10),
            "settled_amount": 100.0,
            "charged_fee": 1.65,
        }
        defaults.update(values)
        return self.env["fee.line"].create(defaults)

    def test_01_line_defaults(self):
        line = self._line()
        self.assertEqual(line.state, "draft")
        self.assertEqual(line.company_id, self.env.company)
        self.assertTrue(line.name.startswith("Fee "))
        self.assertEqual(line.recovered_amount, 0.0)

    def test_02_expected_fee_and_variance(self):
        line = self._line(settled_amount=200.0, charged_fee=3.55)
        self.assertAlmostEqual(line.expected_fee, 3.05, places=2)
        self.assertAlmostEqual(line.variance_amount, 0.50, places=2)

    def test_03_dispute_and_recover(self):
        line = self._line(charged_fee=2.15)
        self.assertTrue(line.action_dispute())
        self.assertEqual(line.state, "disputed")
        self.assertTrue(line.action_recover())
        self.assertEqual(line.state, "recovered")
        self.assertAlmostEqual(line.recovered_amount, line.variance_amount,
                               places=2)

    def test_04_waive_disputed_line(self):
        line = self._line(charged_fee=2.15)
        line.action_dispute()
        self.assertTrue(line.action_waive())
        self.assertEqual(line.state, "waived")

    def test_05_dispute_without_variance_is_refused(self):
        line = self._line(charged_fee=1.65)
        self.assertAlmostEqual(line.variance_amount, 0.0, places=2)
        with self.assertRaises(ValidationError):
            line.action_dispute()

    def test_06_negative_amounts_are_refused(self):
        with self.assertRaises(ValidationError):
            self._line(settled_amount=-10.0)
        with self.assertRaises(ValidationError):
            self._line(charged_fee=-1.0)

    def test_07_contract_counters(self):
        ok_line = self._line(charged_fee=1.65)
        bad_line = self._line(charged_fee=2.15, billed_on=date(2026, 3, 5))
        self.contract.invalidate_recordset()
        self.assertEqual(self.contract.line_count, 2)
        self.assertEqual(self.contract.variance_line_count, 1)
        self.assertTrue(ok_line)
        self.assertTrue(bad_line)

    def test_08_company_isolation(self):
        foreign = self.env["fee.line"].with_company(
            self.other_company).sudo().create({
            "contract_id": self.contract.id,
            "billed_on": date(2026, 4, 12),
            "settled_amount": 50.0,
            "charged_fee": 1.20,
            "company_id": self.other_company.id,
        })
        local = self._line(billed_on=date(2026, 5, 18))
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(local.company_id, self.env.company)
