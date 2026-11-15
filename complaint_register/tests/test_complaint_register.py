# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestComplaintRegister(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "complaint-manager", ["complaint_register.group_complaintreg_user"])
        cls.outsider = cls._user(
            "complaint-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _rec(self):
        return self.env["complaint.register"].create({
            "source": "Customer A",
            "category": "service",
            "severity": "medium",
            "description": "Late response on request.",
            "company_id": self.env.company.id,
        })

    def test_01_flow_resolve_close(self):
        r = self._rec()
        r.action_start()
        self.assertEqual(r.state, "in_progress")
        r.action_resolve()
        self.assertEqual(r.state, "resolved")
        r.action_close()
        self.assertEqual(r.state, "closed")

    def test_02_cancel(self):
        r = self._rec()
        r.action_cancel()
        self.assertEqual(r.state, "cancelled")

    def test_03_state_guards(self):
        r = self._rec()
        with self.assertRaises(UserError):
            r.action_resolve()
        r.action_start()
        with self.assertRaises(UserError):
            r.action_close()

    def test_04_access_control(self):
        r = self._rec()
        with self.assertRaises(Exception):
            self.env["complaint.register"].with_user(self.outsider).create({
                "source": "X",
                "description": "No",
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Cmp B"})
        foreign = self.env["complaint.register"].create({
            "source": "Foreign",
            "description": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["complaint.register"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
