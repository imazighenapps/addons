# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRetainerBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "RetainerBook Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "RetainerBook Test Customer"})
        cls.partner2 = cls.env["res.partner"].create({
            "name": "RetainerBook Second Customer"})

    def _bank(self, **values):
        defaults = {
            "name": "RET-2026-001",
            "partner_id": self.partner.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 12, 31),
            "hours_purchased": 40.0,
            "alert_hours": 5.0,
        }
        defaults.update(values)
        return self.env["retainer.bank"].create(defaults)

    def _usage(self, bank, **values):
        defaults = {
            "bank_id": bank.id,
            "usage_date": date(2026, 2, 10),
            "hours": 4.0,
            "description": "Support session",
        }
        defaults.update(values)
        return self.env["retainer.usage"].create(defaults)

    def test_01_bank_defaults(self):
        bank = self._bank()
        self.assertEqual(bank.state, "open")
        self.assertEqual(bank.company_id, self.env.company)
        self.assertEqual(bank.hours_remaining, 40.0)
        self.assertEqual(bank.burn_rate, 0.0)

    def test_02_usage_updates_balance(self):
        bank = self._bank(hours_purchased=20.0)
        self._usage(bank, hours=5.0, usage_date=date(2026, 3, 1))
        self._usage(bank, hours=3.0, usage_date=date(2026, 3, 15))
        bank.invalidate_recordset()
        self.assertEqual(bank.hours_used, 8.0)
        self.assertEqual(bank.hours_remaining, 12.0)
        self.assertAlmostEqual(bank.burn_rate, 40.0)

    def test_03_usage_cannot_exceed_remaining(self):
        bank = self._bank(hours_purchased=10.0)
        self._usage(bank, hours=6.0, usage_date=date(2026, 4, 1))
        with self.assertRaises(ValidationError):
            self._usage(bank, hours=5.0, usage_date=date(2026, 4, 2))

    def test_04_positive_hours_required(self):
        with self.assertRaises(ValidationError):
            self._bank(name="RET-2026-002", hours_purchased=0)
        bank = self._bank(name="RET-2026-003")
        with self.assertRaises(ValidationError):
            self._usage(bank, hours=0)

    def test_05_dates_constraints(self):
        with self.assertRaises(ValidationError):
            self._bank(name="RET-2026-004", date_start=date(2026, 6, 1),
                       date_end=date(2026, 5, 1))

    def test_06_low_balance_flag(self):
        bank = self._bank(name="RET-2026-005", hours_purchased=10.0, alert_hours=4.0)
        self._usage(bank, hours=7.0, usage_date=date(2026, 5, 1))
        bank.invalidate_recordset()
        self.assertTrue(bank.is_low)
        bank.action_close()
        bank.invalidate_recordset()
        self.assertFalse(bank.is_low)

    def test_07_close_and_reopen(self):
        bank = self._bank(name="RET-2026-006")
        self.assertTrue(bank.action_close())
        self.assertEqual(bank.state, "closed")
        self.assertTrue(bank.action_reopen())
        self.assertEqual(bank.state, "open")
        with self.assertRaises(ValidationError):
            bank.action_reopen()

    def test_08_company_isolation(self):
        other_partner = self.env["res.partner"].with_company(self.other_company).sudo().create({
            "name": "RetainerBook Foreign Customer",
            "company_id": self.other_company.id,
        })
        foreign = self.env["retainer.bank"].with_company(self.other_company).sudo().create({
            "name": "RET-2026-OTH",
            "partner_id": other_partner.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 12, 31),
            "hours_purchased": 30.0,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._bank(name="RET-2026-LOC")
        self.assertNotEqual(local.company_id, foreign.company_id)
