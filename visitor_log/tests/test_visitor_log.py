# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVisitorLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "VisitorLog Other Company"})

    def _visitor(self, **values):
        defaults = {
            "visitor_name": "VisitorLog Test Guest",
            "check_in": datetime(2026, 5, 4, 9, 0),
        }
        defaults.update(values)
        return self.env["visitor.log"].create(defaults)

    def _purge(self, limit):
        wizard = self.env["visitor.purge.wizard"].create({
            "date_limit": limit,
        })
        return wizard.action_purge()

    def test_01_visit_is_created_on_site(self):
        visit = self._visitor(company_name="VisitorLog Test Supplier")
        self.assertEqual(visit.state, "on_site")
        self.assertEqual(visit.check_in, datetime(2026, 5, 4, 9, 0))
        self.assertTrue(visit.name.startswith("Visitor "))
        self.assertEqual(visit.duration_hours, 0.0)

    def test_02_check_out_computes_the_duration(self):
        visit = self._visitor(
            check_in=fields.Datetime.now() - timedelta(hours=2))
        self.assertTrue(visit.action_check_out())
        self.assertEqual(visit.state, "checked_out")
        self.assertTrue(visit.check_out)
        self.assertTrue(1.9 <= visit.duration_hours <= 2.1)
        with self.assertRaises(UserError):
            visit.action_check_out()

    def test_03_check_out_before_check_in_is_refused(self):
        visit = self._visitor()
        with self.assertRaises(ValidationError):
            visit.write({"check_out": datetime(2026, 5, 4, 8, 0)})
        with self.assertRaises(ValidationError):
            self._visitor(
                visitor_name="VisitorLog Test Early Out",
                check_in=datetime(2026, 5, 4, 9, 0),
                check_out=datetime(2026, 5, 4, 8, 0))
        visit.invalidate_recordset()
        self.assertFalse(visit.check_out)

    def test_04_cancel_and_check_in(self):
        visit = self._visitor(state="expected", check_in=False)
        self.assertFalse(visit.check_in)
        self.assertTrue(visit.action_check_in())
        self.assertEqual(visit.state, "on_site")
        self.assertTrue(visit.check_in)
        self.assertTrue(visit.action_cancel())
        self.assertEqual(visit.state, "cancelled")
        gone = self._visitor(visitor_name="VisitorLog Test Gone")
        gone.action_check_out()
        with self.assertRaises(UserError):
            gone.action_cancel()

    def test_05_purge_removes_old_visits(self):
        old = self._visitor(
            visitor_name="VisitorLog Test Old",
            check_in=datetime(2000, 1, 1, 9, 0),
            check_out=datetime(2000, 1, 1, 10, 0),
            state="checked_out")
        self.assertTrue(self._purge(date(2001, 1, 1)))
        self.assertFalse(self.env["visitor.log"].search([
            ("id", "=", old.id)]))

    def test_06_purge_keeps_recent_visits(self):
        recent = self._visitor(
            visitor_name="VisitorLog Test Recent",
            check_in=datetime(2099, 1, 1, 9, 0),
            check_out=datetime(2099, 1, 1, 10, 0),
            state="checked_out")
        on_site = self._visitor(visitor_name="VisitorLog Test Still Here")
        self.assertTrue(self._purge(date(2050, 1, 1)))
        self.assertTrue(recent.exists())
        self.assertTrue(on_site.exists())

    def test_07_defaults_host_and_purpose(self):
        visit = self._visitor()
        self.assertEqual(visit.host_id, self.env.user)
        self.assertEqual(visit.purpose, "meeting")
        self.assertEqual(visit.state, "on_site")
        self.assertEqual(visit.company_id, self.env.company)
        self.assertFalse(visit.company_name)
        self.assertFalse(visit.badge)

    def test_08_company_isolation(self):
        foreign = self.env["visitor.log"].sudo().create({
            "visitor_name": "VisitorLog Test Foreign",
            "company_id": self.other_company.id,
            "host_id": self.env.user.id,
            "check_in": datetime(2000, 1, 1, 9, 0),
            "check_out": datetime(2000, 1, 1, 10, 0),
            "state": "checked_out",
        })
        local = self._visitor(
            visitor_name="VisitorLog Test Local",
            check_in=datetime(2000, 1, 1, 9, 0),
            check_out=datetime(2000, 1, 1, 10, 0),
            state="checked_out")
        self.assertTrue(self._purge(date(2001, 1, 1)))
        self.assertFalse(local.exists())
        self.assertTrue(foreign.exists())
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
