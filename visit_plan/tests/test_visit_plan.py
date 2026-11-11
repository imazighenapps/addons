# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVisitPlan(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "VisitPlan Other Company"})
        cls.partner_a = cls.env["res.partner"].create({
            "name": "VisitPlan Customer Alpha"})
        cls.partner_b = cls.env["res.partner"].create({
            "name": "VisitPlan Customer Beta"})
        cls.tech = cls.env.user

    def _plan(self, **values):
        defaults = {
            "name": "VisitPlan Route 2026-W45",
            "technician_id": self.tech.id,
            "week_start": date(2026, 11, 2),
        }
        defaults.update(values)
        return self.env["visit.plan"].create(defaults)

    def _stop(self, plan, **values):
        defaults = {
            "plan_id": plan.id,
            "partner_id": self.partner_a.id,
            "sequence": 10,
            "planned_date": date(2026, 11, 3),
            "site_name": "VisitPlan Site A",
        }
        defaults.update(values)
        return self.env["visit.stop"].create(defaults)

    def test_01_plan_defaults(self):
        plan = self._plan()
        self.assertEqual(plan.state, "draft")
        self.assertEqual(plan.company_id, self.env.company)
        self.assertEqual(plan.stop_count, 0)
        self.assertEqual(plan.planned_stop_count, 0)
        self.assertEqual(plan.done_stop_count, 0)

    def test_02_stop_defaults_and_name(self):
        plan = self._plan()
        stop = self._stop(plan)
        self.assertEqual(stop.state, "planned")
        self.assertIn(self.partner_a.display_name, stop.name)
        self.assertIn("VisitPlan Site A", stop.name)

    def test_03_plan_requires_stop_before_planning(self):
        plan = self._plan(name="VisitPlan Empty Route")
        with self.assertRaises(ValidationError):
            plan.action_plan()

    def test_04_plan_workflow_and_counts(self):
        plan = self._plan(name="VisitPlan Route 2026-W46",
                          week_start=date(2026, 11, 9))
        stop_a = self._stop(plan, planned_date=date(2026, 11, 10))
        stop_b = self._stop(
            plan, partner_id=self.partner_b.id, sequence=20,
            planned_date=date(2026, 11, 11), site_name="VisitPlan Site B")
        self.assertTrue(plan.action_plan())
        self.assertEqual(plan.state, "planned")
        plan.invalidate_recordset()
        self.assertEqual(plan.stop_count, 2)
        self.assertEqual(plan.planned_stop_count, 2)
        self.assertTrue(stop_a.action_mark_done())
        self.assertEqual(stop_a.state, "done")
        self.assertTrue(stop_a.done_date)
        plan.invalidate_recordset()
        self.assertEqual(plan.done_stop_count, 1)
        self.assertEqual(plan.planned_stop_count, 1)
        self.assertTrue(stop_b.action_mark_done())

    def test_05_close_requires_all_stops_done(self):
        plan = self._plan(name="VisitPlan Route 2026-W47",
                          week_start=date(2026, 11, 16))
        self._stop(plan, planned_date=date(2026, 11, 17))
        plan.action_plan()
        with self.assertRaises(ValidationError):
            plan.action_done()

    def test_06_done_stop_cannot_be_completed_twice(self):
        plan = self._plan(name="VisitPlan Route 2026-W48",
                          week_start=date(2026, 11, 23))
        stop = self._stop(plan, planned_date=date(2026, 11, 24))
        plan.action_plan()
        stop.action_mark_done()
        with self.assertRaises(ValidationError):
            stop.action_mark_done()

    def test_07_stop_done_before_planned_is_refused(self):
        plan = self._plan(name="VisitPlan Route 2026-W49",
                          week_start=date(2026, 11, 30))
        with self.assertRaises(ValidationError):
            self._stop(plan, planned_date=date(2026, 12, 2),
                       done_date=date(2026, 12, 1))

    def test_08_company_isolation(self):
        foreign_tech = self.env["res.users"].with_company(
            self.other_company).sudo().create({
                "name": "VisitPlan Foreign Tech",
                "login": "visit_plan_foreign_tech",
                "company_id": self.other_company.id,
                "company_ids": [(6, 0, [self.other_company.id])],
            })
        foreign_partner = self.env["res.partner"].with_company(
            self.other_company).sudo().create({
                "name": "VisitPlan Foreign Customer",
                "company_id": self.other_company.id,
            })
        foreign_plan = self.env["visit.plan"].with_company(
            self.other_company).sudo().create({
                "name": "VisitPlan Foreign Route",
                "technician_id": foreign_tech.id,
                "week_start": date(2026, 12, 7),
                "company_id": self.other_company.id,
            })
        self.env["visit.stop"].with_company(self.other_company).sudo().create({
            "plan_id": foreign_plan.id,
            "partner_id": foreign_partner.id,
            "planned_date": date(2026, 12, 8),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign_plan.company_id, self.other_company)
        local_plan = self._plan(name="VisitPlan Local Route",
                                week_start=date(2026, 12, 14))
        self._stop(local_plan, planned_date=date(2026, 12, 15))
        self.assertNotEqual(local_plan.company_id, foreign_plan.company_id)

    def test_09_mark_done_closes_route(self):
        plan = self._plan(name="VisitPlan Route 2026-W50",
                          week_start=date(2026, 12, 7))
        stop = self._stop(plan, planned_date=date(2026, 12, 8))
        plan.action_plan()
        stop.action_mark_done()
        self.assertTrue(plan.action_done())
        self.assertEqual(plan.state, "done")
