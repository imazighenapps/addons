# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGiftRegister(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Gift Employee"})
        cls.manager = cls._user(
            "gift-manager", ["gift_register.group_giftregister_user"])
        cls.outsider = cls._user(
            "gift-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _gift(self):
        return self.env["gift.register"].create({
            "direction": "given",
            "counterpart": "Partner Co",
            "description": "Holiday basket",
            "amount": 30.0,
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
        })

    def test_01_flow_declare_approve(self):
        g = self._gift()
        g.action_declare()
        self.assertEqual(g.state, "declared")
        g.action_approve()
        self.assertEqual(g.state, "approved")

    def test_02_refuse(self):
        g = self._gift()
        g.action_declare()
        g.action_refuse()
        self.assertEqual(g.state, "refused")

    def test_03_state_guards(self):
        g = self._gift()
        with self.assertRaises(UserError):
            g.action_approve()
        g.action_declare()
        with self.assertRaises(UserError):
            g.action_declare()

    def test_04_amount_validation(self):
        with self.assertRaises(ValidationError):
            self.env["gift.register"].create({
                "direction": "received",
                "counterpart": "X",
                "description": "Bad",
                "amount": -1.0,
                "company_id": self.env.company.id,
            })

    def test_05_access_control(self):
        g = self._gift()
        with self.assertRaises(Exception):
            self.env["gift.register"].with_user(self.outsider).create({
                "direction": "given",
                "counterpart": "Y",
                "description": "No",
                "company_id": self.env.company.id,
            })
        g.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Gift B"})
        foreign = self.env["gift.register"].create({
            "direction": "given",
            "counterpart": "B",
            "description": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["gift.register"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
