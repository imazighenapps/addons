# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEmployeeOvertime(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "OT Employee"})
        cls.manager = cls._user(
            "overtime-manager", ["employee_overtime.group_employeeover_user"])
        cls.outsider = cls._user(
            "overtime-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _req(self, hours=2.0):
        return self.env["employee.overtime"].create({
            "employee_id": self.employee.id,
            "hours": hours,
            "reason": "Project deadline",
            "company_id": self.env.company.id,
        })

    def test_01_flow_submit_approve(self):
        r = self._req()
        r.action_submit()
        self.assertEqual(r.state, "submitted")
        r.action_approve()
        self.assertEqual(r.state, "approved")

    def test_02_flow_refuse_reset(self):
        r = self._req()
        r.action_submit()
        r.action_refuse()
        self.assertEqual(r.state, "refused")
        r.action_reset()
        self.assertEqual(r.state, "draft")

    def test_03_state_guards(self):
        r = self._req()
        with self.assertRaises(UserError):
            r.action_approve()
        r.action_submit()
        with self.assertRaises(UserError):
            r.action_submit()

    def test_04_hours_validation(self):
        with self.assertRaises(ValidationError):
            self._req(hours=0.0)
        with self.assertRaises(ValidationError):
            self._req(hours=-1.0)

    def test_05_access_control(self):
        r = self._req()
        with self.assertRaises(Exception):
            self.env["employee.overtime"].with_user(self.outsider).create({
                "employee_id": self.employee.id,
                "hours": 1.0,
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "OT B"})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["employee.overtime"].create({
            "employee_id": emp_b.id,
            "hours": 1.0,
            "company_id": company_b.id,
        })
        visible = self.env["employee.overtime"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
