# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestUniformIssueLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Uniform Employee"})
        cls.manager = cls._user(
            "uil-manager",
            ["uniform_issue_log.group_uniformissue_user"])
        cls.outsider = cls._user("uil-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _issue(self, **vals):
        data = {
            "name": vals.pop("name", "UIL-TEST"),
            "employee_id": self.employee.id,
            "item_name": "Test Uniform",
            "quantity": 1,
            "issue_date": self.today,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["uniform.issue.log"].create(data)

    def test_01_create_issue(self):
        rec = self._issue()
        self.assertEqual(rec.state, "draft")

    def test_02_issue_and_return(self):
        rec = self._issue()
        rec.action_issue()
        self.assertEqual(rec.state, "issued")
        rec.action_return()
        self.assertEqual(rec.state, "returned")
        self.assertTrue(rec.return_date)

    def test_03_cancel_and_reset(self):
        rec = self._issue()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._issue()
        with self.assertRaises(UserError):
            rec.action_return()
        rec.action_issue()
        rec.action_return()
        with self.assertRaises(UserError):
            rec.action_cancel()

    def test_05_validation(self):
        with self.assertRaises(ValidationError):
            self._issue(quantity=0)
        with self.assertRaises(ValidationError):
            self._issue(issue_date=self.today, expected_return_date=self.today - timedelta(days=1))

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["uniform.issue.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "employee_id": self.employee.id,
                    "item_name": "No",
                    "company_id": self.env.company.id,
                })
        rec = self._issue(name="UIL-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "UIL B"})
        foreign = self.env["uniform.issue.log"].create({
            "name": "UIL-FOREIGN",
            "employee_id": self.employee.id,
            "item_name": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["uniform.issue.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
