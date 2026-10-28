# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMaintenancePro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.context_today(cls.env.user)
        cls.equipment = cls.env["maint.equipment"].create({
            "name": "CNC Milling Machine",
            "code": "EQ-CNC-01",
            "category": "machine",
            "location": "Plant A - Bay 3",
            "serial_number": "SN-2026-0001",
            "criticality": "high",
            "purchase_date": cls.today - timedelta(days=400),
            "warranty_end": cls.today + timedelta(days=300),
        })

    def _plan(self, **kwargs):
        values = {
            "name": "Quarterly lubrication",
            "equipment_id": self.equipment.id,
            "period_days": 30,
            "task": "Grease the rails and check the coolant level.",
        }
        values.update(kwargs)
        return self.env["maint.plan"].create(values)

    def _request(self, **kwargs):
        values = {
            "equipment_id": self.equipment.id,
            "description": "Hydraulic pump leaking oil on the floor.",
        }
        values.update(kwargs)
        return self.env["maint.request"].create(values)

    def test_01_equipment_lifecycle(self):
        self.assertEqual(self.equipment.state, "running")
        self.equipment.action_stop()
        self.assertEqual(self.equipment.state, "stopped")
        with self.assertRaises(UserError):
            self.equipment.action_stop()
        self.equipment.action_start()
        self.assertEqual(self.equipment.state, "running")
        self.equipment.action_retire()
        self.assertEqual(self.equipment.state, "retired")
        with self.assertRaises(UserError):
            self.equipment.action_retire()
        self.equipment.action_reinstate()
        self.assertEqual(self.equipment.state, "running")

    def test_02_next_date_computed(self):
        plan = self._plan(last_date=date(2026, 1, 1), period_days=30)
        self.assertEqual(plan.next_date, date(2026, 1, 31))
        plan.period_days = 60
        self.assertEqual(plan.next_date, date(2026, 3, 2))
        fresh = self._plan(name="First service", last_date=False,
                           period_days=15)
        self.assertEqual(fresh.next_date, self.today)

    def test_03_cron_generates_and_is_idempotent(self):
        plan = self._plan(last_date=self.today - timedelta(days=45),
                          period_days=30)
        self.assertLessEqual(plan.next_date, self.today)
        created = self.env["maint.plan"]._cron_generate_requests()
        self.assertEqual(created, 1)
        requests = self.env["maint.request"].search([
            ("plan_id", "=", plan.id)])
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests.type, "preventive")
        self.assertEqual(requests.state, "planned")
        self.assertEqual(requests.scheduled_date, self.today)
        self.assertEqual(requests.request_date, self.today)
        self.assertEqual(plan.last_date, self.today)
        self.assertEqual(plan.next_date, self.today + timedelta(days=30))
        created = self.env["maint.plan"]._cron_generate_requests()
        self.assertEqual(created, 0)
        self.assertEqual(self.env["maint.request"].search_count([
            ("plan_id", "=", plan.id)]), 1)
        # An open preventive request created today also blocks a new one.
        guarded = self._plan(name="Monthly inspection",
                             last_date=self.today - timedelta(days=90),
                             period_days=30)
        self._request(plan_id=guarded.id, type="preventive",
                      state="planned", scheduled_date=self.today,
                      description="Preventive job already scheduled.")
        created = self.env["maint.plan"]._cron_generate_requests()
        self.assertEqual(created, 0)
        self.assertEqual(self.env["maint.request"].search_count([
            ("plan_id", "=", guarded.id)]), 1)
        self.assertEqual(guarded.last_date, self.today - timedelta(days=90))

    def test_04_paused_plan_is_skipped(self):
        plan = self._plan(last_date=self.today - timedelta(days=45),
                          period_days=30)
        plan.action_pause()
        self.assertEqual(plan.state, "paused")
        created = self.env["maint.plan"]._cron_generate_requests()
        self.assertEqual(created, 0)
        self.assertFalse(self.env["maint.request"].search([
            ("plan_id", "=", plan.id)]))
        plan.action_resume()
        self.assertEqual(plan.state, "active")
        created = self.env["maint.plan"]._cron_generate_requests()
        self.assertEqual(created, 1)

    def test_05_plan_requires_scheduled_date(self):
        request = self._request()
        self.assertEqual(request.state, "draft")
        self.assertTrue(request.name.startswith("MR/"))
        with self.assertRaises(UserError):
            request.action_plan()
        request.scheduled_date = self.today + timedelta(days=3)
        request.action_plan()
        self.assertEqual(request.state, "planned")

    def test_06_done_requires_duration_and_sets_date(self):
        request = self._request(scheduled_date=self.today)
        request.action_plan()
        request.action_start()
        self.assertEqual(request.state, "in_progress")
        with self.assertRaises(UserError):
            request.action_done()
        self.assertFalse(request.done_date)
        request.duration_hours = 2.5
        request.action_done()
        self.assertEqual(request.state, "done")
        self.assertEqual(request.done_date, self.today)
        self.assertAlmostEqual(request.duration_hours, 2.5, places=2)

    def test_07_done_updates_plan_last_date(self):
        plan = self._plan(last_date=self.today - timedelta(days=40),
                          period_days=30)
        request = self._request(
            plan_id=plan.id, type="preventive",
            scheduled_date=self.today - timedelta(days=2))
        request.action_plan()
        request.duration_hours = 1.0
        request.done_date = self.today - timedelta(days=1)
        request.action_done()
        self.assertEqual(request.state, "done")
        self.assertEqual(request.done_date, self.today - timedelta(days=1))
        self.assertEqual(plan.last_date, self.today - timedelta(days=1))
        self.assertEqual(plan.next_date, self.today + timedelta(days=29))

    def test_08_constraints(self):
        with self.assertRaises(ValidationError):
            self._plan(period_days=-10)
        with self.assertRaises(ValidationError):
            self.env["maint.equipment"].create({
                "name": "Old Press",
                "code": "EQ-PRESS-02",
                "purchase_date": date(2026, 5, 1),
                "warranty_end": date(2026, 4, 1),
            })
        with self.assertRaises(ValidationError):
            self._request(cost=-10.0)
        with self.assertRaises(ValidationError):
            self._request(duration_hours=-1.0)
