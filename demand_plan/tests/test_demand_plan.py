# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestForecastBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ForecastBook Other Company"})
        cls.salesperson = cls.env["res.users"].create({
            "name": "ForecastBook Salesperson",
            "login": "forecastbook_salesperson",
        })

    def _plan(self, **values):
        defaults = {
            "name": "ForecastBook Plan 2026-03",
            "salesperson_id": self.salesperson.id,
            "period_start": date(2026, 3, 1),
            "period_end": date(2026, 3, 31),
        }
        defaults.update(values)
        return self.env["demand.plan"].create(defaults)

    def _add_line(self, plan, **values):
        defaults = {
            "plan_id": plan.id,
            "product_name": "ForecastBook Widget A",
            "forecast_qty": 10.0,
            "actual_qty": 8.0,
            "forecast_amount": 1000.0,
            "actual_amount": 800.0,
        }
        defaults.update(values)
        return self.env["demand.plan.line"].create(defaults)

    def test_01_plan_defaults(self):
        plan = self._plan()
        self.assertEqual(plan.state, "draft")
        self.assertEqual(plan.company_id, self.env.company)
        self.assertEqual(plan.line_count, 0)
        self.assertEqual(plan.variance_qty, 0.0)

    def test_02_line_variance_and_totals(self):
        plan = self._plan()
        line = self._add_line(plan)
        self.assertEqual(line.variance_qty, -2.0)
        self.assertEqual(line.variance_amount, -200.0)
        plan.invalidate_recordset()
        self.assertEqual(plan.line_count, 1)
        self.assertEqual(plan.forecast_qty, 10.0)
        self.assertEqual(plan.actual_qty, 8.0)
        self.assertEqual(plan.variance_amount, -200.0)

    def test_03_commit_close_workflow(self):
        plan = self._plan()
        self._add_line(plan)
        self.assertTrue(plan.action_commit())
        self.assertEqual(plan.state, "committed")
        self.assertTrue(plan.action_close())
        self.assertEqual(plan.state, "closed")

    def test_04_commit_without_lines_is_refused(self):
        plan = self._plan()
        with self.assertRaises(UserError):
            plan.action_commit()

    def test_05_close_requires_committed_state(self):
        plan = self._plan()
        self._add_line(plan)
        with self.assertRaises(UserError):
            plan.action_close()
        plan.action_commit()
        plan.action_close()
        with self.assertRaises(UserError):
            plan.action_close()

    def test_06_reset_to_draft_from_committed(self):
        plan = self._plan(name="ForecastBook Plan 2026-04",
                          period_start=date(2026, 4, 1),
                          period_end=date(2026, 4, 30))
        self._add_line(plan, product_name="ForecastBook Widget B")
        plan.action_commit()
        self.assertTrue(plan.action_reset_draft())
        self.assertEqual(plan.state, "draft")
        plan.action_commit()
        self.assertTrue(plan.action_close())
        self.assertEqual(plan.state, "closed")
        with self.assertRaises(UserError):
            plan.action_reset_draft()

    def test_07_invalid_period_is_refused(self):
        with self.assertRaises(ValidationError):
            self._plan(period_start=date(2026, 5, 10),
                       period_end=date(2026, 5, 1))

    def test_08_forecast_qty_must_be_positive(self):
        plan = self._plan(name="ForecastBook Plan 2026-06",
                          period_start=date(2026, 6, 1),
                          period_end=date(2026, 6, 30))
        with self.assertRaises(ValidationError):
            self._add_line(plan, forecast_qty=0.0)
        with self.assertRaises(ValidationError):
            self._add_line(plan, forecast_qty=-1.0)

    def test_09_company_isolation(self):
        foreign_user = self.env["res.users"].with_company(
            self.other_company).sudo().create({
            "name": "ForecastBook Foreign User",
            "login": "forecastbook_foreign",
            "company_id": self.other_company.id,
            "company_ids": [(6, 0, [self.other_company.id])],
        })
        foreign = self.env["demand.plan"].with_company(
            self.other_company).sudo().create({
            "name": "ForecastBook Foreign Plan",
            "salesperson_id": foreign_user.id,
            "period_start": date(2027, 1, 1),
            "period_end": date(2027, 1, 31),
            "company_id": self.other_company.id,
        })
        local = self._plan(name="ForecastBook Local Plan 2027-01",
                           period_start=date(2027, 1, 1),
                           period_end=date(2027, 1, 31))
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
