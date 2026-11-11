# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReorderPlan(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ReorderPlan Other Company"})

    def _item(self, **values):
        defaults = {
            "name": "CoveragePlan Product A",
            "on_hand_qty": 20.0,
            "daily_demand": 2.0,
            "min_days": 7,
        }
        defaults.update(values)
        return self.env["coverage.item"].create(defaults)

    def test_01_item_defaults(self):
        rec = self._item()
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.company_id, self.env.company)
        self.assertTrue(rec.active)

    def test_02_coverage_days_computed(self):
        rec = self._item(on_hand_qty=20.0, daily_demand=4.0, min_days=7)
        self.assertEqual(rec.coverage_days, 5.0)
        self.assertTrue(rec.below_minimum)

    def test_03_above_minimum_not_flagged(self):
        rec = self._item(on_hand_qty=30.0, daily_demand=2.0, min_days=7)
        self.assertEqual(rec.coverage_days, 15.0)
        self.assertFalse(rec.below_minimum)

    def test_04_plan_and_order_workflow(self):
        rec = self._item(on_hand_qty=5.0, daily_demand=2.0, min_days=7,
                         planned_qty=20.0)
        self.assertTrue(rec.action_plan())
        self.assertEqual(rec.state, "planned")
        self.assertTrue(rec.action_mark_ordered())
        self.assertEqual(rec.state, "ordered")

    def test_05_plan_requires_positive_quantity(self):
        rec = self._item(on_hand_qty=5.0, daily_demand=2.0, min_days=7)
        with self.assertRaises(ValidationError):
            rec.action_plan()

    def test_06_daily_demand_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._item(daily_demand=0.0)
        with self.assertRaises(ValidationError):
            self._item(daily_demand=-1.0)

    def test_07_min_days_and_on_hand_constraints(self):
        with self.assertRaises(ValidationError):
            self._item(min_days=0)
        with self.assertRaises(ValidationError):
            self._item(on_hand_qty=-5.0)

    def test_08_below_minimum_filter(self):
        low = self._item(name="CoveragePlan Low 2026", on_hand_qty=2.0,
                         daily_demand=2.0, min_days=7)
        ok = self._item(name="CoveragePlan OK 2026", on_hand_qty=40.0,
                        daily_demand=2.0, min_days=7)
        found = self.env["coverage.item"].search([
            ("below_minimum", "=", True)])
        self.assertIn(low, found)
        self.assertNotIn(ok, found)

    def test_09_reset_to_draft(self):
        rec = self._item(planned_qty=10.0)
        rec.action_plan()
        self.assertTrue(rec.action_reset_draft())
        self.assertEqual(rec.state, "draft")

    def test_10_company_isolation(self):
        foreign = self.env["coverage.item"].with_company(
            self.other_company).sudo().create({
            "name": "CoveragePlan Foreign 2027",
            "on_hand_qty": 5.0,
            "daily_demand": 1.0,
            "min_days": 10,
            "company_id": self.other_company.id,
        })
        local = self._item(name="CoveragePlan Local 2027")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
