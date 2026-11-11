# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGapWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "GapWatch Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "GapWatch Customer Alpha"})
        cls.partner_b = cls.env["res.partner"].create({
            "name": "GapWatch Customer Beta"})

    def _site(self, **values):
        defaults = {
            "name": "GapWatch Site Alpha",
            "partner_id": self.partner.id,
            "frequency_days": 30,
            "last_visit_date": date(2026, 10, 1),
        }
        defaults.update(values)
        return self.env["visit.site"].create(defaults)

    def test_01_site_defaults(self):
        site = self._site()
        self.assertEqual(site.company_id, self.env.company)
        self.assertTrue(site.active)
        self.assertEqual(site.next_visit_date, date(2026, 10, 31))

    def test_02_overdue_computation(self):
        site = self._site(name="GapWatch Overdue Site",
                          last_visit_date=date(2026, 1, 1),
                          frequency_days=15)
        self.assertTrue(site.is_overdue)
        self.assertEqual(site.next_visit_date, date(2026, 1, 16))
        self.assertGreater(site.overdue_days, 0)

    def test_03_on_track_site(self):
        today = fields.Date.context_today(self.env["visit.site"])
        site = self._site(
            name="GapWatch On Track Site",
            last_visit_date=today - timedelta(days=5),
            frequency_days=30)
        self.assertFalse(site.is_overdue)
        self.assertEqual(site.overdue_days, 0)
        self.assertEqual(site.next_visit_date, today + timedelta(days=25))

    def test_04_mark_visited_refreshes_schedule(self):
        site = self._site(name="GapWatch Refresh Site",
                          last_visit_date=date(2026, 1, 10),
                          frequency_days=10)
        self.assertTrue(site.is_overdue)
        self.assertTrue(site.action_mark_visited())
        self.assertEqual(site.last_visit_date,
                         fields.Date.context_today(site))
        self.assertFalse(site.is_overdue)
        self.assertEqual(site.overdue_days, 0)

    def test_05_frequency_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._site(name="GapWatch Zero Frequency", frequency_days=0)
        with self.assertRaises(ValidationError):
            self._site(name="GapWatch Negative Frequency", frequency_days=-7)

    def test_06_last_visit_is_required(self):
        with self.assertRaises(ValidationError):
            self._site(name="GapWatch No Last Visit", last_visit_date=False)

    def test_07_overdue_filter_and_search(self):
        overdue = self._site(name="GapWatch Filter Overdue",
                             last_visit_date=date(2026, 1, 1),
                             frequency_days=7)
        on_track = self._site(
            name="GapWatch Filter On Track",
            partner_id=self.partner_b.id,
            last_visit_date=fields.Date.context_today(
                self.env["visit.site"]) - timedelta(days=2),
            frequency_days=30)
        found = self.env["visit.site"].search([("is_overdue", "=", True)])
        self.assertIn(overdue, found)
        self.assertNotIn(on_track, found)

    def test_08_company_isolation(self):
        foreign_partner = self.env["res.partner"].with_company(
            self.other_company).sudo().create({
                "name": "GapWatch Foreign Customer",
                "company_id": self.other_company.id,
            })
        foreign = self.env["visit.site"].with_company(
            self.other_company).sudo().create({
                "name": "GapWatch Foreign Site",
                "partner_id": foreign_partner.id,
                "frequency_days": 14,
                "last_visit_date": date(2026, 2, 1),
                "company_id": self.other_company.id,
            })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._site(name="GapWatch Local Site",
                           last_visit_date=date(2026, 3, 1))
        self.assertNotEqual(local.company_id, foreign.company_id)
