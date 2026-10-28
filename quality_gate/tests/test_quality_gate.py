# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestQualityGate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create({
            "name": "QualityGate Test Bearing",
            "type": "consu",
            "is_storable": True,
        })
        cls.plan = cls.env["quality.inspection.plan"].create({
            "name": "Incoming bearing control",
            "code": "QP-TEST-IN-01",
            "operation": "incoming",
            "product_id": cls.product.id,
        })
        cls.point_visual = cls.env["quality.inspection.point"].create({
            "plan_id": cls.plan.id,
            "sequence": 10,
            "name": "Visual aspect",
            "check_type": "pass_fail",
            "instruction": "No burr, no rust, no dent.",
        })
        cls.point_diameter = cls.env["quality.inspection.point"].create({
            "plan_id": cls.plan.id,
            "sequence": 20,
            "name": "Outer diameter",
            "check_type": "range",
            "min_value": 9.8,
            "max_value": 10.2,
            "uom_id": cls.uom_unit.id,
        })

    def _running_plan(self):
        if self.plan.state != "running":
            self.plan.action_start()
        return self.plan

    def _inspection(self):
        return self.env["quality.inspection"].create({
            "plan_id": self._running_plan().id,
            "product_id": self.product.id,
            "quantity": 5.0,
        })

    def _result(self, inspection, point):
        return inspection.result_ids.filtered(
            lambda result: result.point_id == point)

    def test_01_plan_workflow(self):
        self.assertEqual(self.plan.state, "draft")
        self.assertEqual(self.plan.point_count, 2)
        empty = self.env["quality.inspection.plan"].create({
            "name": "Plan without checkpoint",
            "code": "QP-TEST-EMPTY",
        })
        with self.assertRaises(UserError):
            empty.action_start()
        self.plan.action_start()
        self.assertEqual(self.plan.state, "running")
        with self.assertRaises(UserError):
            self.plan.action_reset()
        self.plan.action_pause()
        self.assertEqual(self.plan.state, "paused")
        self.plan.action_resume()
        self.assertEqual(self.plan.state, "running")
        self.plan.action_pause()
        self.plan.action_reset()
        self.assertEqual(self.plan.state, "draft")

    def test_02_start_loads_one_result_per_point(self):
        inspection = self._inspection()
        self.assertTrue(inspection.name.startswith("QI/"))
        self.assertEqual(inspection.state, "draft")
        inspection.action_start()
        self.assertEqual(inspection.state, "in_progress")
        self.assertEqual(inspection.result_count, 2)
        self.assertEqual(inspection.failed_count, 2)
        self.assertEqual(
            set(inspection.result_ids.mapped("point_id").ids),
            set(self.plan.point_ids.ids))
        with self.assertRaises(UserError):
            inspection.action_start()

    def test_03_pass_refused_when_required_result_missing(self):
        inspection = self._inspection()
        inspection.action_start()
        self._result(inspection, self.point_diameter).value_float = 10.0
        self._result(inspection, self.point_visual).unlink()
        with self.assertRaises(UserError):
            inspection.action_pass()
        self.assertEqual(inspection.state, "in_progress")

    def test_04_pass_when_all_required_results_passed(self):
        inspection = self._inspection()
        inspection.action_start()
        for result in inspection.result_ids:
            if result.point_id == self.point_diameter:
                result.value_float = 10.0
            result.passed = True
        inspection.action_pass()
        self.assertEqual(inspection.state, "passed")
        self.assertEqual(inspection.failed_count, 0)

    def test_05_out_of_tolerance_blocks_pass(self):
        inspection = self._inspection()
        inspection.action_start()
        self._result(inspection, self.point_visual).passed = True
        diameter = self._result(inspection, self.point_diameter)
        diameter.value_float = 25.0
        with self.assertRaises(UserError):
            inspection.action_pass()
        self.assertEqual(inspection.state, "in_progress")
        self.assertFalse(diameter.passed)

    def test_06_fail_requires_failed_result_or_note(self):
        inspection = self._inspection()
        with self.assertRaises(UserError):
            inspection.action_fail()
        inspection.note = "Certificate of conformity missing."
        inspection.action_fail()
        self.assertEqual(inspection.state, "failed")
        other = self._inspection()
        other.action_start()
        other.action_fail()
        self.assertEqual(other.state, "failed")

    def test_07_issue_close_sets_date_and_state(self):
        issue = self.env["quality.issue"].create({
            "description": "Burr on the inner ring of the bearing.",
            "severity": "major",
            "product_id": self.product.id,
        })
        self.assertTrue(issue.name.startswith("QN/"))
        self.assertEqual(issue.state, "open")
        issue.action_analyse()
        self.assertEqual(issue.state, "analysis")
        with self.assertRaises(UserError):
            issue.action_close()
        issue.corrective_action = "Add a deburring step at the press."
        issue.action_close()
        self.assertEqual(issue.state, "closed")
        self.assertEqual(
            issue.closed_date, fields.Date.context_today(issue))
        issue.action_reopen()
        self.assertEqual(issue.state, "open")
        self.assertFalse(issue.closed_date)

    def test_08_point_range_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["quality.inspection.point"].create({
                "plan_id": self.plan.id,
                "name": "Inverted tolerance",
                "check_type": "range",
                "min_value": 10.0,
                "max_value": 5.0,
            })
