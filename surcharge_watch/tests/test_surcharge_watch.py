# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSurcharge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "Surcharge Other Company"})
        cls.supplier = cls.env["res.partner"].create({
            "name": "Surcharge Test Supplier 2026"})

    def _clause(self, **values):
        defaults = {
            "name": "Surcharge Steel Clause 2026",
            "partner_id": self.supplier.id,
            "material": "Steel",
            "base_index": 100.0,
            "factor": 2.0,
        }
        defaults.update(values)
        return self.env["surcharge.clause"].create(defaults)

    def _line(self, clause=None, **values):
        defaults = {
            "clause_id": (clause or self._clause()).id,
            "period_start": date(2026, 1, 1),
            "period_end": date(2026, 1, 31),
            "current_index": 110.0,
            "billed_amount": 20.0,
        }
        defaults.update(values)
        return self.env["surcharge.line"].create(defaults)

    def test_01_clause_defaults(self):
        clause = self._clause()
        self.assertEqual(clause.company_id, self.env.company)
        self.assertEqual(clause.line_count, 0)
        self.assertTrue(clause.active)

    def test_02_expected_and_variance(self):
        line = self._line()
        self.assertEqual(line.expected_amount, 20.0)
        self.assertEqual(line.variance_amount, 0.0)
        line.billed_amount = 25.0
        self.assertEqual(line.variance_amount, 5.0)

    def test_03_review_accept_dispute_flow(self):
        line = self._line()
        self.assertEqual(line.state, "draft")
        self.assertTrue(line.action_submit_review())
        self.assertEqual(line.state, "to_review")
        self.assertTrue(line.action_accept())
        self.assertEqual(line.state, "accepted")
        line2 = self._line()
        line2.action_submit_review()
        self.assertTrue(line2.action_dispute())
        self.assertEqual(line2.state, "disputed")

    def test_04_period_and_amount_constraints(self):
        with self.assertRaises(ValidationError):
            self._line(period_start=date(2026, 2, 1),
                       period_end=date(2026, 1, 1))
        with self.assertRaises(ValidationError):
            self._line(current_index=0.0)
        with self.assertRaises(ValidationError):
            self._line(billed_amount=-1.0)

    def test_05_clause_value_constraints(self):
        with self.assertRaises(ValidationError):
            self._clause(name="Bad Base 2026", base_index=0.0)
        with self.assertRaises(ValidationError):
            self._clause(name="Bad Factor 2026", factor=0.0)

    def test_06_reset_and_invalid_transitions(self):
        line = self._line()
        with self.assertRaises(UserError):
            line.action_accept()
        line.action_submit_review()
        self.assertTrue(line.action_reset_draft())
        self.assertEqual(line.state, "draft")

    def test_07_clause_application_counter(self):
        clause = self._clause(name="Surcharge Counter 2026")
        self._line(clause=clause)
        self._line(clause=clause, period_start=date(2026, 2, 1),
                   period_end=date(2026, 2, 28))
        clause.invalidate_recordset()
        self.assertEqual(clause.line_count, 2)

    def test_08_company_isolation(self):
        foreign_supplier = self.env["res.partner"].with_company(
            self.other_company).sudo().create({
            "name": "Surcharge Foreign Supplier 2026"})
        clause = self.env["surcharge.clause"].with_company(
            self.other_company).sudo().create({
            "name": "Foreign Clause 2026",
            "partner_id": foreign_supplier.id,
            "material": "Aluminum",
            "base_index": 120.0,
            "factor": 1.5,
            "company_id": self.other_company.id,
        })
        foreign = self.env["surcharge.line"].with_company(
            self.other_company).sudo().create({
            "clause_id": clause.id,
            "period_start": date(2026, 3, 1),
            "period_end": date(2026, 3, 31),
            "current_index": 130.0,
            "billed_amount": 10.0,
            "company_id": self.other_company.id,
        })
        local = self._line()
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
