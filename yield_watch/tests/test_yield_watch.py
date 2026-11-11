# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestYieldWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "YieldWatch Other Company",
        })
        cls.sample_run = cls.env["yield.run"].create({
            "name": "YW-RUN-2026-001",
            "product_name": "YieldWatch Test Biscuit",
            "run_date": date(2026, 11, 10),
            "planned_qty": 100.0,
            "actual_qty": 92.0,
        })

    def _loss(self, run=None, **values):
        defaults = {
            "run_id": (run or self.sample_run).id,
            "reason": "Scrap",
            "step": "Baking",
            "quantity": 2.0,
        }
        defaults.update(values)
        return self.env["yield.loss"].create(defaults)

    def _started(self, run=None):
        run = run or self.sample_run
        if run.state == "draft":
            run.action_start()
        return run

    def test_01_run_defaults(self):
        run = self.env["yield.run"].create({
            "name": "YW-RUN-DEFAULT",
            "product_name": "YieldWatch Test Default",
            "planned_qty": 50.0,
            "actual_qty": 50.0,
        })
        self.assertEqual(run.state, "draft")
        self.assertEqual(run.company_id, self.env.company)
        self.assertTrue(run.active)
        self.assertEqual(run.responsible_id, self.env.user)

    def test_02_yield_is_computed(self):
        self.assertAlmostEqual(self.sample_run.loss_qty, 8.0, places=2)
        self.assertAlmostEqual(self.sample_run.yield_rate, 92.0, places=2)
        self.sample_run.write({"actual_qty": 80.0})
        self.assertAlmostEqual(self.sample_run.loss_qty, 20.0, places=2)
        self.assertAlmostEqual(self.sample_run.yield_rate, 80.0, places=2)

    def test_03_start_close_reset_workflow(self):
        self.assertEqual(self.sample_run.state, "draft")
        self.assertTrue(self.sample_run.action_start())
        self.assertEqual(self.sample_run.state, "running")
        self.assertTrue(self.sample_run.action_close())
        self.assertEqual(self.sample_run.state, "closed")
        self.assertTrue(self.sample_run.action_reset())
        self.assertEqual(self.sample_run.state, "draft")

    def test_04_invalid_state_transitions(self):
        with self.assertRaises(UserError):
            self.sample_run.action_close()
        with self.assertRaises(UserError):
            self.sample_run.action_reset()
        self._started()
        with self.assertRaises(UserError):
            self.sample_run.action_start()
        self.sample_run.action_close()
        self.assertEqual(self.sample_run.state, "closed")
        self.sample_run.action_reset()
        self.assertEqual(self.sample_run.state, "draft")

    def test_05_quantity_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["yield.run"].create({
                "name": "YW-BAD-PLAN",
                "product_name": "YieldWatch Bad Plan",
                "planned_qty": 0.0,
                "actual_qty": 0.0,
            })
        with self.assertRaises(ValidationError):
            self.sample_run.write({"actual_qty": -1.0})
        with self.assertRaises(ValidationError):
            self.sample_run.write({"actual_qty": 150.0})

    def test_06_loss_lines_update_counters(self):
        self._started()
        self._loss(quantity=3.0, reason="Scrap A")
        self._loss(quantity=5.0, reason="Scrap B", step="Cooling")
        self.sample_run.invalidate_recordset()
        self.assertEqual(self.sample_run.loss_count, 2)
        self.assertAlmostEqual(self.sample_run.line_loss_qty, 8.0, places=2)
        with self.assertRaises(ValidationError):
            self._loss(quantity=0.0, reason="Zero Loss")

    def test_07_closed_run_is_locked(self):
        self._started()
        loss = self._loss(quantity=1.0)
        self.sample_run.action_close()
        with self.assertRaises(UserError):
            self.sample_run.write({"actual_qty": 90.0})
        with self.assertRaises(UserError):
            self._loss(quantity=1.0, reason="Late Loss")
        with self.assertRaises(UserError):
            loss.write({"quantity": 2.0})

    def test_08_company_isolation(self):
        foreign = self.env["yield.run"].with_company(
            self.other_company).sudo().create({
            "name": "YW-FOREIGN",
            "product_name": "YieldWatch Foreign",
            "planned_qty": 10.0,
            "actual_qty": 9.0,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self.env["yield.run"].create({
            "name": "YW-LOCAL",
            "product_name": "YieldWatch Local",
            "planned_qty": 20.0,
            "actual_qty": 19.0,
        })
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
