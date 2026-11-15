# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStaffAwardLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Award Employee"})
        cls.manager = cls._user(
            "sal-manager",
            ["staff_award_log.group_staffawardlo_user"])
        cls.outsider = cls._user("sal-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _award(self, **vals):
        data = {
            "name": vals.pop("name", "SAL-TEST"),
            "employee_id": self.employee.id,
            "award_date": fields.Date.context_today(self.env.user),
            "reason": "Great work",
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["staff.award.log"].create(data)

    def test_01_create_award(self):
        rec = self._award()
        self.assertEqual(rec.state, "draft")

    def test_02_announce_flow(self):
        rec = self._award()
        rec.action_announce()
        self.assertEqual(rec.state, "announced")

    def test_03_cancel_and_reset(self):
        rec = self._award()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._award()
        rec.action_announce()
        with self.assertRaises(UserError):
            rec.action_announce()
        rec = self._award(name="SAL-TEST-2")
        rec.action_cancel()
        with self.assertRaises(UserError):
            rec.action_cancel()

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["staff.award.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "employee_id": self.employee.id,
                    "reason": "No access",
                    "company_id": self.env.company.id,
                })
        rec = self._award(name="SAL-ACC")
        rec.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "SAL B"})
        foreign = self.env["staff.award.log"].create({
            "name": "SAL-FOREIGN",
            "employee_id": self.employee.id,
            "reason": "Foreign award",
            "company_id": company_b.id,
        })
        visible = self.env["staff.award.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
