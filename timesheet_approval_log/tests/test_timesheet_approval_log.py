# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTimesheetApprovalLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "TSA Employee"})
        cls.today = fields.Date.context_today(cls.env.user)
        cls.manager = cls._user(
            "tsa-manager",
            ["timesheet_approval_log.group_timesheetapp_user"])
        cls.outsider = cls._user("tsa-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _log(self, **vals):
        data = {
            "name": vals.pop("name", "TSA-TEST"),
            "employee_id": self.employee.id,
            "date_start": self.today - timedelta(days=7),
            "date_end": self.today,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["timesheet.approval.log"].create(data)

    def test_01_create_log(self):
        log = self._log()
        self.assertEqual(log.state, "draft")
        self.assertEqual(log.total_hours, 0.0)

    def test_02_total_hours_computed(self):
        project = self.env["project.project"].create({"name": "TSA Project"})
        self.env["account.analytic.line"].create({
            "name": "Work A",
            "employee_id": self.employee.id,
            "project_id": project.id,
            "date": self.today - timedelta(days=3),
            "unit_amount": 4.0,
        })
        self.env["account.analytic.line"].create({
            "name": "Work B",
            "employee_id": self.employee.id,
            "project_id": project.id,
            "date": self.today - timedelta(days=2),
            "unit_amount": 3.5,
        })
        log = self._log()
        self.assertAlmostEqual(log.total_hours, 7.5, places=2)

    def test_03_state_flow_approve(self):
        log = self._log()
        log.action_submit()
        self.assertEqual(log.state, "submitted")
        self.assertTrue(log.submitted_date)
        log.action_approve()
        self.assertEqual(log.state, "approved")
        self.assertTrue(log.approved_date)
        self.assertEqual(log.approver_id, self.env.user)

    def test_04_reject_and_resubmit(self):
        log = self._log()
        log.action_submit()
        log.action_reject()
        self.assertEqual(log.state, "rejected")
        log.action_submit()
        self.assertEqual(log.state, "submitted")

    def test_05_invalid_transitions(self):
        log = self._log()
        with self.assertRaises(UserError):
            log.action_approve()
        log.action_submit()
        with self.assertRaises(UserError):
            log.action_submit()

    def test_06_end_before_start_is_refused(self):
        with self.assertRaises(ValidationError):
            self._log(
                date_start=self.today,
                date_end=self.today - timedelta(days=1),
            )

    def test_07_access_control(self):
        with self.assertRaises(Exception):
            self.env["timesheet.approval.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "employee_id": self.employee.id,
                    "date_start": self.today - timedelta(days=7),
                    "date_end": self.today,
                    "company_id": self.env.company.id,
                })
        log = self._log(name="TSA-ACC")
        log.with_user(self.manager).read()

    def test_08_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "TSA B"})
        foreign = self.env["timesheet.approval.log"].create({
            "name": "TSA-FOREIGN",
            "employee_id": self.employee.id,
            "date_start": self.today - timedelta(days=7),
            "date_end": self.today,
            "company_id": company_b.id,
        })
        visible = self.env["timesheet.approval.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
