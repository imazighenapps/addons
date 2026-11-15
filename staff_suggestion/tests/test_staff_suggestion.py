# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStaffSuggestion(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Idea Employee"})
        cls.manager = cls._user(
            "suggest-manager", ["staff_suggestion.group_staffsuggest_user"])
        cls.outsider = cls._user(
            "suggest-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _sug(self):
        return self.env["staff.suggestion"].create({
            "name": "Improve lighting",
            "employee_id": self.employee.id,
            "description": "Add better lighting in warehouse aisles.",
            "expected_benefit": "Fewer picking errors.",
            "company_id": self.env.company.id,
        })

    def test_01_flow_accept_done(self):
        s = self._sug()
        s.action_submit()
        s.action_review()
        s.action_accept()
        self.assertEqual(s.state, "accepted")
        s.action_done()
        self.assertEqual(s.state, "done")

    def test_02_flow_reject(self):
        s = self._sug()
        s.action_submit()
        s.action_review()
        s.action_reject()
        self.assertEqual(s.state, "rejected")

    def test_03_state_guards(self):
        s = self._sug()
        with self.assertRaises(UserError):
            s.action_review()
        s.action_submit()
        with self.assertRaises(UserError):
            s.action_accept()

    def test_04_access_control(self):
        s = self._sug()
        with self.assertRaises(Exception):
            self.env["staff.suggestion"].with_user(self.outsider).create({
                "name": "No",
                "description": "x",
                "company_id": self.env.company.id,
            })
        s.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Sug B"})
        foreign = self.env["staff.suggestion"].create({
            "name": "Foreign",
            "description": "Foreign idea",
            "company_id": company_b.id,
        })
        visible = self.env["staff.suggestion"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
