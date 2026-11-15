# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestExitInterviewLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Exit Employee"})
        cls.manager = cls._user(
            "exit-manager", ["exit_interview_log.group_exitintervie_user"])
        cls.outsider = cls._user(
            "exit-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _rec(self):
        return self.env["exit.interview.log"].create({
            "employee_id": self.employee.id,
            "departure_reason": "career",
            "feedback": "Looking for growth.",
            "company_id": self.env.company.id,
        })

    def test_01_flow_complete_review(self):
        r = self._rec()
        r.action_complete()
        self.assertEqual(r.state, "completed")
        r.action_review()
        self.assertEqual(r.state, "reviewed")
        r.action_reset()
        self.assertEqual(r.state, "draft")

    def test_02_state_guards(self):
        r = self._rec()
        with self.assertRaises(UserError):
            r.action_review()
        r.action_complete()
        with self.assertRaises(UserError):
            r.action_complete()

    def test_03_access_control(self):
        r = self._rec()
        with self.assertRaises(Exception):
            self.env["exit.interview.log"].with_user(self.outsider).create({
                "employee_id": self.employee.id,
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_04_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Exit B"})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["exit.interview.log"].create({
            "employee_id": emp_b.id,
            "company_id": company_b.id,
        })
        visible = self.env["exit.interview.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)

    def test_05_fields(self):
        r = self._rec()
        self.assertTrue(r.name)
        self.assertEqual(r.departure_reason, "career")
