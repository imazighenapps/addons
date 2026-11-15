# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWorkPermitRecord(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Permit Employee"})
        cls.manager = cls._user(
            "permit-manager", ["work_permit_record.group_workpermitre_user"])
        cls.outsider = cls._user(
            "permit-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _permit(self, **kw):
        vals = {
            "name": "Work Authorization",
            "employee_id": self.employee.id,
            "permit_type": "work_permit",
            "company_id": self.env.company.id,
        }
        vals.update(kw)
        return self.env["work.permit.record"].create(vals)

    def test_01_mark_expired_and_reset(self):
        p = self._permit()
        p.action_mark_expired()
        self.assertEqual(p.state, "expired")
        p.action_reset()
        self.assertEqual(p.state, "valid")

    def test_02_cancel(self):
        p = self._permit()
        p.action_cancel()
        self.assertEqual(p.state, "cancelled")
        with self.assertRaises(UserError):
            p.action_mark_expired()

    def test_03_expiry_flag(self):
        today = fields.Date.context_today(self.env.user)
        p = self._permit(date_expiry=today - timedelta(days=1))
        self.assertTrue(p.is_expired)

    def test_04_date_validation(self):
        today = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self._permit(date_issue=today, date_expiry=today - timedelta(days=1))

    def test_05_access_control(self):
        p = self._permit()
        with self.assertRaises(Exception):
            self.env["work.permit.record"].with_user(self.outsider).create({
                "name": "No",
                "employee_id": self.employee.id,
                "company_id": self.env.company.id,
            })
        p.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Permit B"})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["work.permit.record"].create({
            "name": "Foreign",
            "employee_id": emp_b.id,
            "company_id": company_b.id,
        })
        visible = self.env["work.permit.record"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
