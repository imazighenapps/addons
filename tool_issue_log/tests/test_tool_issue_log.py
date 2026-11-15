# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestToolIssueLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tool = cls.env["tool.item"].create({
            "name": "DRILL-01", "category": "Power tools", "company_id": cls.env.company.id,
        })
        cls.employee = cls.env["hr.employee"].create({"name": "Tool Employee"})
        cls.manager = cls._user(
            "toolissue-manager", ["tool_issue_log.group_toolissuelog_user"])
        cls.outsider = cls._user(
            "toolissue-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _issue(self):
        return self.env["tool.issue"].create({
            "tool_id": self.tool.id,
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
        })

    def test_01_issue_return(self):
        i = self._issue()
        self.assertEqual(i.state, "issued")
        i.action_return()
        self.assertEqual(i.state, "returned")
        self.assertTrue(i.date_return)

    def test_02_reset(self):
        i = self._issue()
        i.action_return()
        i.action_reset()
        self.assertEqual(i.state, "issued")

    def test_03_invalid_transitions(self):
        i = self._issue()
        with self.assertRaises(UserError):
            i.action_reset()
        i.action_return()
        with self.assertRaises(UserError):
            i.action_return()

    def test_04_date_validation(self):
        today = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self.env["tool.issue"].create({
                "tool_id": self.tool.id,
                "employee_id": self.employee.id,
                "date_issue": today,
                "date_return": today.replace(year=today.year - 1),
                "company_id": self.env.company.id,
            })

    def test_05_access_control(self):
        i = self._issue()
        with self.assertRaises(Exception):
            self.env["tool.issue"].with_user(self.outsider).create({
                "tool_id": self.tool.id,
                "employee_id": self.employee.id,
                "company_id": self.env.company.id,
            })
        i.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Tool B"})
        tool_b = self.env["tool.item"].create({"name": "TB", "company_id": company_b.id})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["tool.issue"].create({
            "tool_id": tool_b.id,
            "employee_id": emp_b.id,
            "company_id": company_b.id,
        })
        visible = self.env["tool.issue"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
