# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestItAccessRequest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Access Employee"})
        cls.manager = cls._user(
            "accessreq-manager", ["it_access_request.group_itaccessrequ_user"])
        cls.outsider = cls._user(
            "accessreq-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _req(self):
        return self.env["it.access.request"].create({
            "employee_id": self.employee.id,
            "system_name": "ERP Reporting",
            "access_type": "read",
            "justification": "Need reporting access.",
            "company_id": self.env.company.id,
        })

    def test_01_flow_grant_revoke(self):
        r = self._req()
        r.action_submit()
        r.action_approve()
        self.assertEqual(r.state, "approved")
        r.action_grant()
        self.assertEqual(r.state, "granted")
        self.assertTrue(r.date_granted)
        r.action_revoke()
        self.assertEqual(r.state, "revoked")
        self.assertTrue(r.date_revoked)

    def test_02_refuse(self):
        r = self._req()
        r.action_submit()
        r.action_refuse()
        self.assertEqual(r.state, "refused")

    def test_03_state_guards(self):
        r = self._req()
        with self.assertRaises(UserError):
            r.action_approve()
        r.action_submit()
        with self.assertRaises(UserError):
            r.action_grant()
        r.action_approve()
        with self.assertRaises(UserError):
            r.action_submit()

    def test_04_access_control(self):
        r = self._req()
        with self.assertRaises(Exception):
            self.env["it.access.request"].with_user(self.outsider).create({
                "system_name": "No",
                "access_type": "read",
                "justification": "x",
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Acc B"})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["it.access.request"].create({
            "employee_id": emp_b.id,
            "system_name": "Foreign",
            "access_type": "read",
            "justification": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["it.access.request"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
