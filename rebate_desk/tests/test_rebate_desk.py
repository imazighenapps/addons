# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRebateBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "RebateBook Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "RebateBook Test Customer"})
        cls.other_partner = cls.env["res.partner"].create({
            "name": "RebateBook Test Other Customer"})
        cls.contract = cls.env["rebate.contract"].create({
            "name": "RebateBook 2026 Contract",
            "partner_id": cls.partner.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 12, 31),
            "rate": 3.0,
            "target_amount": 100000.0,
        })

    def _accrual(self, amount=500.0, accrual_date=date(2026, 6, 15),
                 **values):
        defaults = {
            "name": "RebateBook Accrual",
            "contract_id": self.contract.id,
            "accrual_date": accrual_date,
            "invoice_ref": "RB-INV-2026-001",
            "amount": amount,
        }
        defaults.update(values)
        return self.env["rebate.accrual"].create(defaults)

    def test_01_contract_defaults(self):
        self.assertEqual(self.contract.state, "open")
        self.assertEqual(self.contract.company_id, self.env.company)
        self.assertEqual(self.contract.accrued_amount, 0.0)
        self.assertEqual(self.contract.remaining_amount, 0.0)
        self.assertEqual(self.contract.accrual_count, 0)

    def test_02_accrual_updates_totals(self):
        line = self._accrual(amount=750.0)
        self.contract.invalidate_recordset()
        self.assertEqual(self.contract.accrued_amount, 750.0)
        self.assertEqual(self.contract.remaining_amount, 750.0)
        self.assertEqual(self.contract.accrual_count, 1)
        self.assertEqual(line.state, "open")

    def test_03_multiple_accruals_sum(self):
        self._accrual(amount=200.0, accrual_date=date(2026, 3, 10),
                      invoice_ref="RB-INV-2026-002")
        self._accrual(amount=300.0, accrual_date=date(2026, 7, 20),
                      invoice_ref="RB-INV-2026-003")
        self.contract.invalidate_recordset()
        self.assertEqual(self.contract.accrued_amount, 500.0)
        self.assertEqual(self.contract.accrual_count, 2)

    def test_04_settle_contract(self):
        self._accrual(amount=400.0)
        self.assertTrue(self.contract.action_settle())
        self.assertEqual(self.contract.state, "settled")
        self.assertTrue(self.contract.settled_on)
        self.assertEqual(self.contract.remaining_amount, 0.0)
        self.assertTrue(all(
            line.state == "settled" for line in self.contract.accrual_ids))

    def test_05_double_settle_is_refused(self):
        self.contract.action_settle()
        with self.assertRaises(ValidationError):
            self.contract.action_settle()

    def test_06_rate_must_be_valid(self):
        with self.assertRaises(ValidationError):
            self.env["rebate.contract"].create({
                "name": "RebateBook Bad Rate",
                "partner_id": self.partner.id,
                "date_start": date(2026, 1, 1),
                "date_end": date(2026, 12, 31),
                "rate": 0.0,
            })

    def test_07_dates_and_amount_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["rebate.contract"].create({
                "name": "RebateBook Bad Dates",
                "partner_id": self.partner.id,
                "date_start": date(2026, 12, 31),
                "date_end": date(2026, 1, 1),
                "rate": 2.0,
            })
        with self.assertRaises(ValidationError):
            self._accrual(amount=0.0)
        with self.assertRaises(ValidationError):
            self._accrual(accrual_date=date(2027, 2, 1))

    def test_08_company_isolation(self):
        foreign_partner = self.env["res.partner"].sudo().create({
            "name": "RebateBook Foreign Customer"})
        foreign = self.env["rebate.contract"].with_company(
            self.other_company).sudo().create({
            "name": "RebateBook Foreign Contract",
            "partner_id": foreign_partner.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 12, 31),
            "rate": 1.5,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(self.contract.company_id, self.env.company)
