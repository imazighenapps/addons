# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestKeyIssueLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Key Employee"})
        cls.manager = cls._user(
            "kil-manager",
            ["key_issue_log.group_keyissuelog_user"])
        cls.outsider = cls._user("kil-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _record(self, **vals):
        data = {
            "name": vals.pop("name", "KIL-TEST"),
            "key_label": "Test Key",
            "employee_id": self.employee.id,
            "issue_date": self.today,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["key.issue.log"].create(data)

    def test_01_create_record(self):
        rec = self._record()
        self.assertEqual(rec.state, "draft")

    def test_02_issue_and_return(self):
        rec = self._record()
        rec.action_issue()
        self.assertEqual(rec.state, "issued")
        rec.action_return()
        self.assertEqual(rec.state, "returned")
        self.assertTrue(rec.return_date)

    def test_03_lost_and_reset(self):
        rec = self._record()
        rec.action_issue()
        rec.action_lost()
        self.assertEqual(rec.state, "lost")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._record()
        with self.assertRaises(UserError):
            rec.action_return()
        rec.action_issue()
        with self.assertRaises(UserError):
            rec.action_issue()

    def test_05_date_validation(self):
        with self.assertRaises(ValidationError):
            self._record(
                issue_date=self.today,
                expected_return_date=self.today - timedelta(days=1),
            )

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["key.issue.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "key_label": "No",
                    "company_id": self.env.company.id,
                })
        rec = self._record(name="KIL-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "KIL B"})
        foreign = self.env["key.issue.log"].create({
            "name": "KIL-FOREIGN",
            "key_label": "Foreign Key",
            "company_id": company_b.id,
        })
        visible = self.env["key.issue.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
