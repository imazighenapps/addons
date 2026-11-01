# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBudgetCtlPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.budget = cls.env["budget.ctl"].create({
            "name": "BudgetCtlPro Test Marketing",
            "code": "BGT-TEST-001",
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 12, 31),
            "line_ids": [
                (0, 0, {
                    "name": "Advertising",
                    "planned": 10000.0,
                    "actual": 2500.0,
                    "committed": 1500.0,
                }),
                (0, 0, {
                    "name": "Events",
                    "planned": 6000.0,
                    "actual": 1000.0,
                    "committed": 500.0,
                }),
            ],
        })

    def _budget(self, **kwargs):
        values = {
            "name": "BudgetCtlPro Test Budget",
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 6, 30),
        }
        values.update(kwargs)
        return self.env["budget.ctl"].create(values)

    def _line(self, budget, name, planned=0.0, actual=0.0, committed=0.0):
        return self.env["budget.ctl.line"].create({
            "budget_id": budget.id,
            "name": name,
            "planned": planned,
            "actual": actual,
            "committed": committed,
        })

    def _started(self):
        if self.budget.state == "draft":
            self.budget.action_start()
        return self.budget

    def test_01_available_is_planned_minus_actual_minus_committed(self):
        self.assertAlmostEqual(self.budget.total_planned, 16000.0, places=2)
        self.assertAlmostEqual(self.budget.total_actual, 3500.0, places=2)
        self.assertAlmostEqual(self.budget.total_committed, 2000.0, places=2)
        self.assertAlmostEqual(self.budget.total_available, 10500.0, places=2)
        line = self.budget.line_ids.filtered(
            lambda item: item.name == "Advertising")
        self.assertAlmostEqual(line.available, 6000.0, places=2)
        line.write({"committed": 4000.0})
        self.assertAlmostEqual(line.available, 3500.0, places=2)
        self.budget.invalidate_recordset()
        self.assertAlmostEqual(self.budget.total_available, 8000.0, places=2)

    def test_02_overspend_is_flagged(self):
        self.assertFalse(self.budget.is_overspent)
        budget = self._budget(name="BudgetCtlPro Test Overspend")
        self._line(budget, "Consulting", planned=1000.0, actual=800.0,
                   committed=300.0)
        self.assertAlmostEqual(budget.total_available, -100.0, places=2)
        self.assertTrue(budget.is_overspent)
        budget.line_ids.write({"planned": 2000.0})
        self.assertAlmostEqual(budget.total_available, 900.0, places=2)
        self.assertFalse(budget.is_overspent)

    def test_03_negative_planned_amount_is_refused(self):
        self._line(self.budget, "Credit note", actual=-250.0)
        self.budget.invalidate_recordset()
        self.assertAlmostEqual(self.budget.total_actual, 3250.0, places=2)
        line = self.budget.line_ids.filtered(
            lambda item: item.name == "Advertising")
        with self.assertRaises(ValidationError):
            self._line(self.budget, "Negative plan", planned=-1.0)
        with self.assertRaises(ValidationError):
            self._line(self.budget, "Negative commitment", committed=-5.0)
        with self.assertRaises(ValidationError):
            line.write({"planned": -10.0})

    def test_04_close_locks_the_budget_and_its_lines(self):
        with self.assertRaises(UserError):
            self.budget.action_close()
        self._started()
        self.assertTrue(self.budget.action_close())
        self.assertEqual(self.budget.state, "closed")
        with self.assertRaises(UserError):
            self._line(self.budget, "Late line", planned=100.0)
        line = self.budget.line_ids[0]
        with self.assertRaises(UserError):
            line.write({"planned": 20000.0})
        with self.assertRaises(UserError):
            line.unlink()
        with self.assertRaises(UserError):
            self.budget.write({"date_end": date(2027, 6, 30)})
        self.budget.write({"note": "Frozen after closing."})
        self.assertEqual(self.budget.note, "Frozen after closing.")

    def test_05_dates_must_be_coherent(self):
        same_day = self._budget(
            name="BudgetCtlPro Test Same Day",
            date_start=date(2026, 3, 1),
            date_end=date(2026, 3, 1),
        )
        self.assertEqual(same_day.date_start, same_day.date_end)
        with self.assertRaises(ValidationError):
            self._budget(
                name="BudgetCtlPro Test Bad Dates",
                date_start=date(2026, 12, 31),
                date_end=date(2026, 1, 1),
            )
        with self.assertRaises(ValidationError):
            self.budget.write({"date_start": date(2027, 1, 1)})

    def test_06_code_is_unique_per_company(self):
        with self.assertRaises(ValidationError):
            self._budget(name="BudgetCtlPro Test Duplicate",
                         code="BGT-TEST-001")
        generated = self._budget(name="BudgetCtlPro Test Sequenced")
        self.assertTrue(generated.code.startswith("BGT/"))
        other = self._budget(name="BudgetCtlPro Test Sequenced Again")
        self.assertNotEqual(generated.code, other.code)

    def test_07_totals_are_the_sum_of_the_lines(self):
        budget = self._budget(name="BudgetCtlPro Test Totals")
        self.assertAlmostEqual(budget.total_planned, 0.0, places=2)
        self.assertAlmostEqual(budget.total_available, 0.0, places=2)
        self.assertFalse(budget.is_overspent)
        self._line(budget, "Line A", planned=1000.0, actual=100.0,
                   committed=50.0)
        self._line(budget, "Line B", planned=2000.0, actual=200.0,
                   committed=150.0)
        self._line(budget, "Line C", planned=500.0, actual=50.0,
                   committed=25.0)
        budget.invalidate_recordset()
        self.assertAlmostEqual(budget.total_planned, 3500.0, places=2)
        self.assertAlmostEqual(budget.total_actual, 350.0, places=2)
        self.assertAlmostEqual(budget.total_committed, 225.0, places=2)
        self.assertAlmostEqual(budget.total_available, 2925.0, places=2)
        budget.line_ids[0].unlink()
        self.assertAlmostEqual(budget.total_planned, 2500.0, places=2)

    def test_08_reset_returns_to_draft(self):
        with self.assertRaises(UserError):
            self.budget.action_reset()
        self._started()
        self.assertTrue(self.budget.action_close())
        self.assertTrue(self.budget.action_reset())
        self.assertEqual(self.budget.state, "draft")
        line = self.budget.line_ids[0]
        line.write({"planned": 12000.0})
        self.assertAlmostEqual(line.planned, 12000.0, places=2)
        with self.assertRaises(UserError):
            self.budget.action_close()
        self.assertTrue(self.budget.action_start())
        self.assertEqual(self.budget.state, "running")
