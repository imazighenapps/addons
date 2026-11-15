# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOnboardingChecklist(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "New Hire"})
        cls.manager = cls._user(
            "onboarding-manager", ["onboarding_checklist_log.group_onboardingch_user"])
        cls.outsider = cls._user(
            "onboarding-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _rec(self):
        return self.env["onboarding.checklist"].create({
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
            "line_ids": [(0, 0, {"name": "Create email account"})],
        })

    def test_01_flow_start_done(self):
        r = self._rec()
        r.action_start()
        self.assertEqual(r.state, "in_progress")
        r.action_done()
        self.assertEqual(r.state, "done")

    def test_02_start_requires_lines(self):
        r = self.env["onboarding.checklist"].create({
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
        })
        with self.assertRaises(UserError):
            r.action_start()

    def test_03_state_guards(self):
        r = self._rec()
        with self.assertRaises(UserError):
            r.action_done()
        r.action_start()
        with self.assertRaises(UserError):
            r.action_start()

    def test_04_access_control(self):
        r = self._rec()
        with self.assertRaises(Exception):
            self.env["onboarding.checklist"].with_user(self.outsider).create({
                "employee_id": self.employee.id,
                "company_id": self.env.company.id,
                "line_ids": [(0, 0, {"name": "x"})],
            })
        r.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Onb B"})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["onboarding.checklist"].create({
            "employee_id": emp_b.id,
            "company_id": company_b.id,
            "line_ids": [(0, 0, {"name": "Foreign"})],
        })
        visible = self.env["onboarding.checklist"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
