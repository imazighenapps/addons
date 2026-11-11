# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPremiumWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "PremiumWatch Other Company"})
        cls.currency = cls.env.company.currency_id

    def _entry(self, **values):
        defaults = {
            "name": "EXP-2026-001",
            "product_name": "PremiumWatch Part A",
            "requester_name": "PremiumWatch Team Alpha",
            "reason": "Line stoppage risk",
            "urgency_type": "expedited",
            "request_date": date(2026, 6, 8),
            "normal_cost": 100.0,
            "actual_cost": 140.0,
            "currency_id": self.currency.id,
        }
        defaults.update(values)
        return self.env["expedite.entry"].create(defaults)

    def test_01_entry_defaults(self):
        rec = self._entry()
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.company_id, self.env.company)
        self.assertTrue(rec.has_premium)

    def test_02_premium_computed(self):
        rec = self._entry(normal_cost=100.0, actual_cost=160.0)
        self.assertEqual(rec.premium_amount, 60.0)
        self.assertTrue(rec.has_premium)

    def test_03_no_premium_when_not_higher(self):
        rec = self._entry(normal_cost=100.0, actual_cost=90.0)
        self.assertEqual(rec.premium_amount, 0.0)
        self.assertFalse(rec.has_premium)

    def test_04_confirm_workflow(self):
        rec = self._entry()
        self.assertTrue(rec.action_confirm())
        self.assertEqual(rec.state, "confirmed")
        with self.assertRaises(ValidationError):
            rec.action_confirm()

    def test_05_reset_to_draft(self):
        rec = self._entry()
        rec.action_confirm()
        self.assertTrue(rec.action_reset_draft())
        self.assertEqual(rec.state, "draft")

    def test_06_negative_costs_refused(self):
        with self.assertRaises(ValidationError):
            self._entry(normal_cost=-1.0)
        with self.assertRaises(ValidationError):
            self._entry(actual_cost=-5.0)

    def test_07_has_premium_filter(self):
        premium = self._entry(name="EXP-2026-002", actual_cost=150.0)
        flat = self._entry(name="EXP-2026-003", normal_cost=100.0,
                           actual_cost=100.0)
        found = self.env["expedite.entry"].search([
            ("has_premium", "=", True)])
        self.assertIn(premium, found)
        self.assertNotIn(flat, found)

    def test_08_grouping_fields_present(self):
        rec = self._entry(requester_name="PremiumWatch Team Beta",
                          urgency_type="emergency")
        self.assertEqual(rec.requester_name, "PremiumWatch Team Beta")
        self.assertEqual(rec.urgency_type, "emergency")

    def test_09_company_isolation(self):
        foreign = self.env["expedite.entry"].with_company(
            self.other_company).sudo().create({
            "name": "EXP-2027-F1",
            "product_name": "PremiumWatch Foreign Part",
            "requester_name": "PremiumWatch Foreign Team",
            "reason": "Urgent export",
            "urgency_type": "emergency",
            "request_date": date(2027, 2, 14),
            "normal_cost": 80.0,
            "actual_cost": 120.0,
            "currency_id": self.other_company.currency_id.id,
            "company_id": self.other_company.id,
        })
        local = self._entry(name="EXP-2027-L1")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
