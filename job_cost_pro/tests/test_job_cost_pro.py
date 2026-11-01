# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestJobCostPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "JobCostPro Test Customer",
            "is_company": True,
        })
        cls.vendor = cls.env["res.partner"].create({
            "name": "JobCostPro Test Vendor",
            "is_company": True,
            "supplier_rank": 1,
        })
        cls.project = cls.env["project.project"].create({
            "name": "JobCostPro Test Renovation",
        })
        cls.job = cls.env["job.cost"].create({
            "name": "JobCostPro Test Office Fit-out",
            "code": "JOB-TEST-001",
            "partner_id": cls.partner.id,
            "project_id": cls.project.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 12, 31),
            "budget_revenue": 120000.0,
            "budget_cost": 90000.0,
        })

    def _line(self, amount, cost_type="material", committed=False, **kwargs):
        values = {
            "job_id": self.job.id,
            "date": date(2026, 3, 1),
            "cost_type": cost_type,
            "description": "%s cost line" % cost_type.title(),
            "amount": amount,
            "is_committed": committed,
            "partner_id": self.vendor.id,
        }
        values.update(kwargs)
        return self.env["job.cost.line"].create(values)

    def _started(self):
        if self.job.state == "draft":
            self.job.action_start()
        return self.job

    def test_01_start_requires_a_budget(self):
        job = self.env["job.cost"].create({
            "name": "JobCostPro Test No Budget",
            "code": "JOB-TEST-NOBUDGET",
            "date_start": date(2026, 1, 1),
        })
        self.assertEqual(job.state, "draft")
        with self.assertRaises(UserError):
            job.action_start()
        self.assertEqual(job.state, "draft")
        job.write({"budget_cost": 25000.0})
        self.assertTrue(job.action_start())
        self.assertEqual(job.state, "running")
        with self.assertRaises(UserError):
            job.action_start()

    def test_02_committed_and_actual_costs_are_separate(self):
        self._started()
        self._line(12000.0, "labor")
        self._line(4000.0, "material")
        self._line(8000.0, "subcontract", committed=True)
        self._line(1500.0, "overhead", committed=True)
        self.assertAlmostEqual(self.job.actual_cost, 16000.0, places=2)
        self.assertAlmostEqual(self.job.committed_cost, 9500.0, places=2)
        material = self.job.line_ids.filtered(
            lambda line: line.cost_type == "material")
        self.assertEqual(len(material), 1)
        material.write({"is_committed": True})
        self.assertAlmostEqual(self.job.actual_cost, 12000.0, places=2)
        self.assertAlmostEqual(self.job.committed_cost, 13500.0, places=2)
        self.assertTrue(self.job.action_recompute())
        self.assertAlmostEqual(self.job.actual_cost, 12000.0, places=2)
        self.assertAlmostEqual(self.job.committed_cost, 13500.0, places=2)

    def test_03_margin_and_margin_rate(self):
        self._started()
        self.job.write({"actual_revenue": 50000.0})
        self._line(20000.0, "labor")
        self._line(5000.0, "material", committed=True)
        self.assertAlmostEqual(self.job.margin, 25000.0, places=2)
        self.assertAlmostEqual(self.job.margin_rate, 50.0, places=2)
        no_revenue = self.env["job.cost"].create({
            "name": "JobCostPro Test No Revenue",
            "code": "JOB-TEST-NOREV",
            "budget_cost": 10000.0,
        })
        self.env["job.cost.line"].create({
            "job_id": no_revenue.id,
            "date": date(2026, 2, 1),
            "cost_type": "labor",
            "description": "Labor before any invoice",
            "amount": 1000.0,
        })
        self.assertAlmostEqual(no_revenue.margin, -1000.0, places=2)
        self.assertEqual(no_revenue.margin_rate, 0.0)

    def test_04_progress_is_bounded(self):
        self._started()
        self._line(36000.0, "labor")
        self.assertAlmostEqual(self.job.progress_pct, 40.0, places=2)
        self._line(90000.0, "subcontract", committed=True)
        self.assertAlmostEqual(self.job.progress_pct, 100.0, places=2)
        with self.assertRaises(ValidationError):
            self.job.write({"progress_pct": 150.0})

    def test_05_overrun_alert(self):
        self._started()
        self._line(80000.0, "labor")
        self.assertFalse(self.job.is_overrun)
        self._line(18500.0, "material", committed=True)
        self.assertFalse(self.job.is_overrun)
        self._line(1000.0, "other", committed=True)
        self.assertTrue(self.job.is_overrun)
        self.job.write({"alert_threshold": 20.0})
        self.assertFalse(self.job.is_overrun)
        self._line(9000.0, "subcontract", committed=True)
        self.assertTrue(self.job.is_overrun)

    def test_06_close_locks_lines_and_budget(self):
        with self.assertRaises(UserError):
            self.job.action_close()
        self._started()
        line = self._line(5000.0, "labor")
        self.assertTrue(self.job.action_close())
        self.assertEqual(self.job.state, "closed")
        with self.assertRaises(UserError):
            self.job.write({"budget_cost": 95000.0})
        with self.assertRaises(UserError):
            self.job.write({"budget_revenue": 130000.0})
        with self.assertRaises(UserError):
            self._line(1000.0, "other")
        with self.assertRaises(UserError):
            line.write({"amount": 6000.0})
        with self.assertRaises(UserError):
            line.unlink()
        self.job.write({"note": "Closed after the final invoice."})
        self.assertEqual(self.job.note, "Closed after the final invoice.")
        self.assertTrue(self.job.action_reset())
        self.assertEqual(self.job.state, "draft")
        self._line(1000.0, "other")
        with self.assertRaises(UserError):
            self.job.action_reset()

    def test_07_code_is_unique_per_company(self):
        with self.assertRaises(ValidationError):
            self.env["job.cost"].create({
                "name": "JobCostPro Test Duplicate",
                "code": "JOB-TEST-001",
            })
        with self.assertRaises(ValidationError):
            self.env["job.cost"].create([
                {"name": "JobCostPro Test Batch A",
                 "code": "JOB-TEST-BATCH"},
                {"name": "JobCostPro Test Batch B",
                 "code": "JOB-TEST-BATCH"},
            ])
        other_company = self.env["res.company"].create({
            "name": "JobCostPro Test Company",
        })
        other = self.env["job.cost"].create({
            "name": "JobCostPro Test Other Company",
            "code": "JOB-TEST-001",
            "company_id": other_company.id,
        })
        self.assertEqual(other.code, "JOB-TEST-001")

    def test_08_dates_must_be_coherent(self):
        with self.assertRaises(ValidationError):
            self.env["job.cost"].create({
                "name": "JobCostPro Test Bad Dates",
                "code": "JOB-TEST-BADDATES",
                "date_start": date(2026, 12, 31),
                "date_end": date(2026, 1, 1),
            })
        one_day = self.env["job.cost"].create({
            "name": "JobCostPro Test One Day",
            "code": "JOB-TEST-ONEDAY",
            "date_start": date(2026, 5, 1),
            "date_end": date(2026, 5, 1),
        })
        self.assertEqual(one_day.date_end, one_day.date_start)
        with self.assertRaises(ValidationError):
            one_day.write({"date_end": date(2025, 1, 1)})
        with self.assertRaises(ValidationError):
            self._line(-10.0, "labor", description="Negative cost line")
        with self.assertRaises(ValidationError):
            self.env["job.cost"].create({
                "name": "JobCostPro Test Negative Budget",
                "code": "JOB-TEST-NEGBUDGET",
                "budget_cost": -500.0,
            })
