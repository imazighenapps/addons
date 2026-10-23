# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCleaning(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({
            "name": "Demo Building Co", "is_company": True})
        cls.agent = cls.env["cleaning.agent"].create({
            "name": "Demo Agent", "hourly_rate": 18.0, "monthly_salary": 1800.0})
        cls.site_visit = cls.env["cleaning.site"].create({
            "name": "Head Office", "partner_id": cls.customer.id,
            "billing_mode": "visit", "price_per_visit": 220.0,
        })
        cls.site_area = cls.env["cleaning.site"].create({
            "name": "Warehouse Annex", "partner_id": cls.customer.id,
            "billing_mode": "area", "area": 400.0, "price_per_m2": 0.35,
        })

    def test_01_sequence(self):
        visit = self.env["cleaning.visit"].create({
            "site_id": self.site_visit.id, "agent_id": self.agent.id})
        self.assertTrue(visit.name.startswith("VIS-"))
        self.assertEqual(visit.state, "planned")

    def test_02_pricing_per_visit(self):
        self.assertEqual(self.site_visit.visit_price(), 220.0)
        self.assertEqual(self.site_area.visit_price(), 140.0)

    def test_03_price_pulled_into_visit(self):
        visit = self.env["cleaning.visit"].create({
            "site_id": self.site_area.id, "agent_id": self.agent.id})
        self.assertEqual(visit.price, 140.0)

    def test_04_checkin_out_flow(self):
        visit = self.env["cleaning.visit"].create({
            "site_id": self.site_visit.id, "agent_id": self.agent.id})
        with self.assertRaises(UserError):
            visit.action_check_out()
        visit.action_check_in()
        self.assertEqual(visit.state, "in_progress")
        with self.assertRaises(UserError):
            visit.action_check_in()
        visit.action_check_out()
        self.assertEqual(visit.state, "done")
        self.assertTrue(visit.check_out)

    def test_05_plan_next_date(self):
        plan = self.env["cleaning.plan"].create({
            "name": "Daily HQ", "site_id": self.site_visit.id,
            "frequency": "daily", "agent_id": self.agent.id})
        self.assertEqual(plan.next_date, date.today() + timedelta(days=1))
        monthly = self.env["cleaning.plan"].create({
            "name": "Monthly Warehouse", "site_id": self.site_area.id,
            "frequency": "monthly", "agent_id": self.agent.id})
        self.assertTrue(monthly.next_date > date.today())

    def test_06_invoice_requires_completion(self):
        visit = self.env["cleaning.visit"].create({
            "site_id": self.site_visit.id, "agent_id": self.agent.id})
        with self.assertRaises(UserError):
            visit.action_create_invoice()
        visit.action_check_in()
        visit.action_check_out()
        visit.action_create_invoice()
        self.assertTrue(visit.invoice_id)
        self.assertEqual(visit.state, "invoiced")
        with self.assertRaises(UserError):
            visit.action_create_invoice()

    def test_07_site_and_agent_stats(self):
        plan = self.env["cleaning.plan"].create({
            "name": "Daily HQ", "site_id": self.site_visit.id,
            "frequency": "daily", "agent_id": self.agent.id})
        self.site_visit.agent_ids = [(4, self.agent.id)]
        visit = self.env["cleaning.visit"].create({
            "site_id": self.site_visit.id, "agent_id": self.agent.id,
            "plan_id": plan.id})
        visit.action_check_in()
        visit.action_check_out()
        self.site_visit.invalidate_recordset()
        self.agent.invalidate_recordset()
        plan.invalidate_recordset()
        self.assertEqual(self.site_visit.visit_count, 1)
        self.assertTrue(self.site_visit.last_visit_date)
        self.assertEqual(self.agent.sites_count, 1)
        self.assertEqual(plan.visits_done, 1)