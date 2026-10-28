# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProjectMargin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "ProjectMargin Test Customer",
        })
        cls.project = cls.env["margin.project"].create({
            "name": "ProjectMargin Test Website",
            "code": "PM-TEST-001",
            "partner_id": cls.partner.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 12, 31),
            "budget_revenue": 100000.0,
            "budget_cost": 80000.0,
        })

    def _line(self, line_type, amount, **kwargs):
        values = {
            "project_id": self.project.id,
            "line_type": line_type,
            "description": "%s line" % line_type.title(),
            "amount": amount,
        }
        values.update(kwargs)
        return self.env["margin.line"].create(values)

    def _started(self):
        if self.project.state == "draft":
            self.project.action_start()
        return self.project

    def test_01_start_requires_a_budget(self):
        project = self.env["margin.project"].create({
            "name": "ProjectMargin Test Empty",
            "code": "PM-TEST-EMPTY",
        })
        self.assertEqual(project.state, "draft")
        with self.assertRaises(UserError):
            project.action_start()
        self.assertEqual(project.state, "draft")
        project.write({"budget_cost": 15000.0})
        self.assertTrue(project.action_start())
        self.assertEqual(project.state, "running")
        with self.assertRaises(UserError):
            project.action_start()

    def test_02_lines_update_the_actuals(self):
        self._started()
        self._line("revenue", 60000.0, description="Phase 1 invoice")
        self._line("revenue", 20000.0, description="Phase 2 invoice")
        self._line("cost", 45000.0, category="labor")
        self._line("cost", 5000.0, category="expense")
        self.assertAlmostEqual(self.project.actual_revenue, 80000.0, places=2)
        self.assertAlmostEqual(self.project.actual_cost, 50000.0, places=2)
        self.assertAlmostEqual(self.project.actual_margin, 30000.0, places=2)
        self.assertAlmostEqual(self.project.margin_rate, 37.5, places=2)

    def test_03_budget_margin_and_cost_ratio(self):
        self._started()
        self.assertAlmostEqual(self.project.budget_margin, 20000.0, places=2)
        self.assertEqual(self.project.cost_ratio, 0.0)
        self._line("cost", 40000.0, category="labor")
        self.assertAlmostEqual(self.project.cost_ratio, 50.0, places=2)
        no_cost_budget = self.env["margin.project"].create({
            "name": "ProjectMargin Test No Cost Budget",
            "code": "PM-TEST-NOCOST",
            "budget_revenue": 5000.0,
        })
        self.assertEqual(no_cost_budget.cost_ratio, 0.0)
        self.assertAlmostEqual(
            no_cost_budget.budget_margin, 5000.0, places=2)

    def test_04_overrun_threshold(self):
        self._started()
        self._line("cost", 88000.0, category="subcontract")
        self.assertFalse(self.project.is_overrun)
        self._line("cost", 1000.0, category="material")
        self.assertTrue(self.project.is_overrun)
        self.project.write({"alert_threshold": 20.0})
        self.assertFalse(self.project.is_overrun)

    def test_05_close_and_reset(self):
        with self.assertRaises(UserError):
            self.project.action_close()
        self._started()
        self.assertTrue(self.project.action_close())
        self.assertEqual(self.project.state, "closed")
        with self.assertRaises(UserError):
            self.project.action_close()
        self.assertTrue(self.project.action_reset())
        self.assertEqual(self.project.state, "draft")
        with self.assertRaises(UserError):
            self.project.action_reset()

    def test_06_closed_project_budget_is_locked(self):
        self._started()
        self.project.action_close()
        with self.assertRaises(UserError):
            self.project.write({"budget_cost": 90000.0})
        with self.assertRaises(UserError):
            self.project.write({"budget_revenue": 120000.0})
        self.assertAlmostEqual(self.project.budget_cost, 80000.0, places=2)
        self.project.write({"note": "Budget frozen after closing."})
        self.assertEqual(self.project.note, "Budget frozen after closing.")
        self.assertEqual(self.project.state, "closed")

    def test_07_closed_project_lines_are_locked(self):
        self._started()
        line = self._line("cost", 1000.0, category="other")
        self.project.action_close()
        with self.assertRaises(UserError):
            self._line("cost", 2000.0)
        with self.assertRaises(UserError):
            line.write({"amount": 3000.0})

    def test_08_constraints(self):
        with self.assertRaises(ValidationError):
            self._line("cost", -10.0, description="Negative cost")
        with self.assertRaises(ValidationError):
            self.env["margin.project"].create({
                "name": "ProjectMargin Test Bad Dates",
                "code": "PM-TEST-BADDATES",
                "date_start": date(2026, 12, 31),
                "date_end": date(2026, 1, 1),
            })
        with self.assertRaises(ValidationError):
            self.env["margin.project"].create({
                "name": "ProjectMargin Test Negative Budget",
                "code": "PM-TEST-NEGBUDGET",
                "budget_revenue": -1000.0,
            })
        with self.assertRaises(ValidationError):
            self.env["margin.project"].create({
                "name": "ProjectMargin Test Duplicate Code",
                "code": "PM-TEST-001",
            })
