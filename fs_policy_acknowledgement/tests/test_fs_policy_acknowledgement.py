# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPolicyAcknowledgement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.policy = cls.env["hr.policy"].create({
            "name": "Code of Conduct", "version": "1.0", "company_id": cls.env.company.id,
        })
        cls.employee = cls.env["hr.employee"].create({"name": "Ack Employee"})
        cls.manager = cls._user(
            "policyack-manager", ["fs_policy_acknowledgement.group_fspolicyackn_user"])
        cls.outsider = cls._user(
            "policyack-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _ack(self):
        return self.env["policy.acknowledgement"].create({
            "policy_id": self.policy.id,
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
        })

    def test_01_acknowledge_and_reset(self):
        a = self._ack()
        self.assertEqual(a.state, "pending")
        a.action_acknowledge()
        self.assertEqual(a.state, "acknowledged")
        self.assertTrue(a.date_ack)
        a.action_reset()
        self.assertEqual(a.state, "pending")
        self.assertFalse(a.date_ack)

    def test_02_unique_employee_policy(self):
        self._ack()
        with self.assertRaises(Exception):
            self._ack()

    def test_03_access_control(self):
        a = self._ack()
        with self.assertRaises(Exception):
            self.env["policy.acknowledgement"].with_user(self.outsider).create({
                "policy_id": self.policy.id,
                "employee_id": self.employee.id,
                "company_id": self.env.company.id,
            })
        a.with_user(self.manager).read()

    def test_04_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Policy B"})
        policy_b = self.env["hr.policy"].create({"name": "Policy B1", "company_id": company_b.id})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["policy.acknowledgement"].create({
            "policy_id": policy_b.id,
            "employee_id": emp_b.id,
            "company_id": company_b.id,
        })
        visible = self.env["policy.acknowledgement"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)

    def test_05_policy_fields(self):
        self.assertEqual(self.policy.name, "Code of Conduct")
        self.assertTrue(self.policy.active)
