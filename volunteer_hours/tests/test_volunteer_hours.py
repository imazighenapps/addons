# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVolunteerHours(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.volunteer = cls.env["res.partner"].create({"name": "Demo Volunteer"})
        cls.manager = cls._user(
            "volunteer-manager", ["volunteer_hours.group_volunteerhou_user"])
        cls.outsider = cls._user(
            "volunteer-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _entry(self, hours=3.0):
        return self.env["volunteer.hours"].create({
            "volunteer_id": self.volunteer.id,
            "hours": hours,
            "activity": "Community support",
            "company_id": self.env.company.id,
        })

    def test_01_flow_submit_validate(self):
        e = self._entry()
        e.action_submit()
        self.assertEqual(e.state, "submitted")
        e.action_validate()
        self.assertEqual(e.state, "validated")
        e.action_reset()
        self.assertEqual(e.state, "draft")

    def test_02_state_guards(self):
        e = self._entry()
        with self.assertRaises(UserError):
            e.action_validate()
        e.action_submit()
        with self.assertRaises(UserError):
            e.action_submit()

    def test_03_hours_validation(self):
        with self.assertRaises(ValidationError):
            self._entry(hours=0.0)

    def test_04_access_control(self):
        e = self._entry()
        with self.assertRaises(Exception):
            self.env["volunteer.hours"].with_user(self.outsider).create({
                "volunteer_id": self.volunteer.id,
                "hours": 1.0,
                "activity": "X",
                "company_id": self.env.company.id,
            })
        e.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Vol B"})
        vol_b = self.env["res.partner"].create({"name": "Vol B", "company_id": company_b.id})
        foreign = self.env["volunteer.hours"].create({
            "volunteer_id": vol_b.id,
            "hours": 2.0,
            "activity": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["volunteer.hours"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
