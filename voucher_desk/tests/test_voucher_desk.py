# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVoucherBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "VoucherBook Other Company"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "VoucherBook Test Employee"})
        cls.employee2 = cls.env["hr.employee"].create({
            "name": "VoucherBook Second Employee"})

    def _period(self, **values):
        defaults = {
            "name": "Voucher 2026-05",
            "date_start": date(2026, 5, 1),
            "date_end": date(2026, 5, 31),
            "working_days": 20,
            "voucher_value": 8.0,
        }
        defaults.update(values)
        return self.env["voucher.period"].create(defaults)

    def _allocation(self, period, employee=None, **values):
        defaults = {
            "period_id": period.id,
            "employee_id": (employee or self.employee).id,
            "worked_days": 18,
        }
        defaults.update(values)
        return self.env["voucher.allocation"].create(defaults)

    def test_01_period_defaults(self):
        period = self._period()
        self.assertEqual(period.state, "draft")
        self.assertEqual(period.company_id, self.env.company)
        self.assertEqual(period.total_vouchers, 0)

    def test_02_allocation_computes_vouchers(self):
        period = self._period(voucher_value=10.0)
        line = self._allocation(period, worked_days=15)
        self.assertEqual(line.vouchers_earned, 15)
        self.assertEqual(line.amount_value, 150.0)

    def test_03_period_total_is_stored(self):
        period = self._period()
        self._allocation(period, employee=self.employee, worked_days=18)
        self._allocation(period, employee=self.employee2, worked_days=20)
        period.invalidate_recordset()
        self.assertEqual(period.total_vouchers, 38)

    def test_04_worked_days_cannot_exceed_period(self):
        period = self._period(working_days=20)
        with self.assertRaises(ValidationError):
            self._allocation(period, worked_days=21)

    def test_05_negative_worked_days_refused(self):
        period = self._period()
        with self.assertRaises(ValidationError):
            self._allocation(period, worked_days=-1)

    def test_06_validate_and_reset(self):
        period = self._period(name="Voucher 2026-06",
                              date_start=date(2026, 6, 1), date_end=date(2026, 6, 30))
        self.assertTrue(period.action_validate())
        self.assertEqual(period.state, "validated")
        self.assertTrue(period.action_reset_draft())
        self.assertEqual(period.state, "draft")

    def test_07_period_dates_and_values_checked(self):
        with self.assertRaises(ValidationError):
            self._period(name="Voucher 2026-07", date_start=date(2026, 7, 10),
                         date_end=date(2026, 7, 1))
        with self.assertRaises(ValidationError):
            self._period(name="Voucher 2026-08", working_days=0)
        with self.assertRaises(ValidationError):
            self._period(name="Voucher 2026-09", voucher_value=0)

    def test_08_company_isolation(self):
        other_emp = self.env["hr.employee"].with_company(self.other_company).sudo().create({
            "name": "VoucherBook Foreign Employee",
            "company_id": self.other_company.id,
        })
        foreign_period = self.env["voucher.period"].with_company(self.other_company).sudo().create({
            "name": "Voucher 2026-10 OTH",
            "date_start": date(2026, 10, 1),
            "date_end": date(2026, 10, 31),
            "working_days": 22,
            "voucher_value": 7.5,
            "company_id": self.other_company.id,
        })
        foreign_line = self.env["voucher.allocation"].with_company(self.other_company).sudo().create({
            "period_id": foreign_period.id,
            "employee_id": other_emp.id,
            "worked_days": 20,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign_period.company_id, self.other_company)
        self.assertEqual(foreign_line.company_id, self.other_company)
        local = self._period(name="Voucher 2026-11")
        self.assertNotEqual(local.company_id, foreign_period.company_id)
