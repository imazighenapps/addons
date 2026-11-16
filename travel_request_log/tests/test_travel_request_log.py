# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTravelRequestLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Travel Employee"})
        cls.manager = cls._user(
            "trl-manager",
            ["travel_request_log.group_travelreques_user"])
        cls.outsider = cls._user("trl-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _req(self, **vals):
        data = {
            "name": vals.pop("name", "TRL-TEST"),
            "employee_id": self.employee.id,
            "destination": "Test City",
            "date_start": self.today,
            "date_end": self.today + timedelta(days=1),
            "purpose": "Test purpose",
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["travel.request.log"].create(data)

    def test_01_create_request(self):
        rec = self._req()
        self.assertEqual(rec.state, "draft")

    def test_02_approve_complete_flow(self):
        rec = self._req()
        rec.action_submit()
        self.assertEqual(rec.state, "submitted")
        rec.action_approve()
        self.assertEqual(rec.state, "approved")
        rec.action_complete()
        self.assertEqual(rec.state, "completed")

    def test_03_reject_and_reset(self):
        rec = self._req()
        rec.action_submit()
        rec.action_reject()
        self.assertEqual(rec.state, "rejected")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._req()
        with self.assertRaises(UserError):
            rec.action_approve()
        rec.action_submit()
        with self.assertRaises(UserError):
            rec.action_complete()

    def test_05_date_validation(self):
        with self.assertRaises(ValidationError):
            self._req(date_start=self.today, date_end=self.today - timedelta(days=1))

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["travel.request.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "employee_id": self.employee.id,
                    "destination": "X",
                    "date_start": self.today,
                    "date_end": self.today,
                    "purpose": "No",
                    "company_id": self.env.company.id,
                })
        rec = self._req(name="TRL-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "TRL B"})
        foreign = self.env["travel.request.log"].create({
            "name": "TRL-FOREIGN",
            "employee_id": self.employee.id,
            "destination": "Y",
            "date_start": self.today,
            "date_end": self.today,
            "purpose": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["travel.request.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
