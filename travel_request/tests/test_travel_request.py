# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTravelRequest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Travel Employee"})
        cls.manager = cls._user(
            "travelreq-manager", ["travel_request.group_travelreques_user"])
        cls.outsider = cls._user(
            "travelreq-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _req(self):
        today = fields.Date.context_today(self.env.user)
        return self.env["travel.request"].create({
            "employee_id": self.employee.id,
            "destination": "Paris",
            "purpose": "Client meeting",
            "date_start": today,
            "date_end": today + timedelta(days=2),
            "estimated_cost": 500.0,
            "company_id": self.env.company.id,
        })

    def test_01_flow_approve_done(self):
        r = self._req()
        r.action_submit()
        r.action_approve()
        self.assertEqual(r.state, "approved")
        r.action_done()
        self.assertEqual(r.state, "done")

    def test_02_refuse(self):
        r = self._req()
        r.action_submit()
        r.action_refuse()
        self.assertEqual(r.state, "refused")

    def test_03_state_guards(self):
        r = self._req()
        with self.assertRaises(UserError):
            r.action_approve()
        r.action_submit()
        with self.assertRaises(UserError):
            r.action_done()

    def test_04_date_validation(self):
        today = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self.env["travel.request"].create({
                "employee_id": self.employee.id,
                "destination": "X",
                "purpose": "X",
                "date_start": today,
                "date_end": today - timedelta(days=1),
                "company_id": self.env.company.id,
            })

    def test_05_access_control(self):
        r = self._req()
        with self.assertRaises(Exception):
            self.env["travel.request"].with_user(self.outsider).create({
                "employee_id": self.employee.id,
                "destination": "No",
                "purpose": "No",
                "date_start": fields.Date.context_today(self.env.user),
                "date_end": fields.Date.context_today(self.env.user),
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Travel B"})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        today = fields.Date.context_today(self.env.user)
        foreign = self.env["travel.request"].create({
            "employee_id": emp_b.id,
            "destination": "B",
            "purpose": "Foreign",
            "date_start": today,
            "date_end": today,
            "company_id": company_b.id,
        })
        visible = self.env["travel.request"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
