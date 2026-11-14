# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestKeyCustody(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.item = cls.env["key.item"].create({
            "name": "KEY-001", "key_type": "key", "company_id": cls.env.company.id,
        })
        cls.employee = cls.env["hr.employee"].create({"name": "Key Holder"})
        cls.manager = cls._user(
            "keycustody-manager", ["key_custody.group_keycustody_user"])
        cls.outsider = cls._user(
            "keycustody-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _custody(self):
        return self.env["key.custody"].create({
            "item_id": self.item.id,
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
        })

    def test_01_issue_and_return(self):
        c = self._custody()
        self.assertEqual(c.state, "issued")
        c.action_return()
        self.assertEqual(c.state, "returned")
        self.assertTrue(c.date_return)

    def test_02_mark_lost(self):
        c = self._custody()
        c.action_lost()
        self.assertEqual(c.state, "lost")

    def test_03_invalid_transitions(self):
        c = self._custody()
        c.action_return()
        with self.assertRaises(UserError):
            c.action_return()

    def test_04_date_validation(self):
        today = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self.env["key.custody"].create({
                "item_id": self.item.id,
                "employee_id": self.employee.id,
                "date_issue": today,
                "date_return": today.replace(year=today.year - 1),
                "company_id": self.env.company.id,
            })

    def test_05_access_control(self):
        c = self._custody()
        with self.assertRaises(Exception):
            self.env["key.custody"].with_user(self.outsider).create({
                "item_id": self.item.id,
                "employee_id": self.employee.id,
                "company_id": self.env.company.id,
            })
        c.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Key B"})
        item_b = self.env["key.item"].create({"name": "KEY-B", "company_id": company_b.id})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["key.custody"].create({
            "item_id": item_b.id,
            "employee_id": emp_b.id,
            "company_id": company_b.id,
        })
        visible = self.env["key.custody"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
