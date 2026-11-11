# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLateFeeCalc(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "LateFee Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "LateFee Test Customer"})
        cls.rule = cls.env["late.fee.rule"].create({
            "name": "LateFee Test Rule",
            "annual_rate": 12.0,
            "fixed_fee": 40.0,
        })

    def _line(self, **values):
        defaults = {
            "name": "LATE-INV-2026-001",
            "rule_id": self.rule.id,
            "partner_id": self.partner.id,
            "due_date": date(2026, 1, 31),
            "calculation_date": date(2026, 3, 2),
            "base_amount": 1000.0,
        }
        defaults.update(values)
        return self.env["late.fee.line"].create(defaults)

    def test_01_line_defaults(self):
        line = self._line(name="LATE-DEF-001")
        self.assertEqual(line.state, "draft")
        self.assertEqual(line.company_id, self.env.company)
        self.assertFalse(line.issued_on)
        self.assertGreaterEqual(line.days_late, 0)

    def test_02_interest_computation(self):
        line = self._line(
            name="LATE-CALC-001",
            due_date=date(2026, 1, 1),
            calculation_date=date(2026, 1, 31),
            base_amount=3650.0,
        )
        # 3650 * 12% * 30/365 + 40 = 36 + 40 = 76
        self.assertEqual(line.days_late, 30)
        self.assertAlmostEqual(line.interest_amount, 76.0, places=2)

    def test_03_zero_days_no_interest(self):
        line = self._line(
            name="LATE-ZERO-001",
            due_date=date(2026, 2, 10),
            calculation_date=date(2026, 2, 10),
        )
        self.assertEqual(line.days_late, 0)
        self.assertAlmostEqual(line.interest_amount, 0.0, places=2)

    def test_04_issue_workflow(self):
        line = self._line(
            name="LATE-ISSUE-001",
            due_date=date(2026, 1, 1),
            calculation_date=date(2026, 2, 1),
        )
        self.assertTrue(line.action_issue())
        self.assertEqual(line.state, "issued")
        self.assertTrue(line.issued_on)
        with self.assertRaises(ValidationError):
            line.action_issue()

    def test_05_cannot_issue_zero_interest(self):
        line = self._line(
            name="LATE-NOINT-001",
            due_date=date(2026, 3, 10),
            calculation_date=date(2026, 3, 10),
        )
        with self.assertRaises(ValidationError):
            line.action_issue()

    def test_06_amount_and_date_constraints(self):
        with self.assertRaises(ValidationError):
            self._line(name="LATE-BAD-AMT", base_amount=0.0)
        with self.assertRaises(ValidationError):
            self._line(name="LATE-BAD-AMT2", base_amount=-10.0)
        with self.assertRaises(ValidationError):
            self._line(
                name="LATE-BAD-DATE",
                due_date=date(2026, 3, 10),
                calculation_date=date(2026, 3, 1),
            )

    def test_07_rule_totals_and_constraints(self):
        line = self._line(
            name="LATE-TOT-001",
            due_date=date(2026, 1, 1),
            calculation_date=date(2026, 2, 1),
        )
        line.action_issue()
        self.rule.invalidate_recordset()
        self.assertGreater(self.rule.issued_amount, 0.0)
        self.assertEqual(self.rule.line_count, 1)
        with self.assertRaises(ValidationError):
            self.env["late.fee.rule"].create({
                "name": "LateFee Bad Rate",
                "annual_rate": -1.0,
            })

    def test_08_company_isolation(self):
        foreign_rule = self.env["late.fee.rule"].with_company(
            self.other_company).sudo().create({
            "name": "LateFee Foreign Rule",
            "annual_rate": 8.0,
            "company_id": self.other_company.id,
        })
        foreign_partner = self.env["res.partner"].with_company(
            self.other_company).sudo().create({
            "name": "LateFee Foreign Customer"})
        foreign = self.env["late.fee.line"].with_company(
            self.other_company).sudo().create({
            "name": "LATE-FOREIGN-001",
            "rule_id": foreign_rule.id,
            "partner_id": foreign_partner.id,
            "due_date": date(2026, 1, 31),
            "calculation_date": date(2026, 3, 2),
            "base_amount": 500.0,
            "company_id": self.other_company.id,
        })
        local = self._line(name="LATE-LOCAL-001")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
