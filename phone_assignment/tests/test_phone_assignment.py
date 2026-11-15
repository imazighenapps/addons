# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPhoneAssignment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.item = cls.env["phone.item"].create({
            "name": "PH-001", "phone_number": "+1000001", "item_type": "phone",
            "company_id": cls.env.company.id,
        })
        cls.employee = cls.env["hr.employee"].create({"name": "Phone Employee"})
        cls.manager = cls._user(
            "phoneassign-manager", ["phone_assignment.group_phoneassignm_user"])
        cls.outsider = cls._user(
            "phoneassign-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _assign(self):
        return self.env["phone.assignment"].create({
            "item_id": self.item.id,
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
        })

    def test_01_assign_return(self):
        a = self._assign()
        self.assertEqual(a.state, "assigned")
        a.action_return()
        self.assertEqual(a.state, "returned")
        self.assertTrue(a.date_return)

    def test_02_mark_lost(self):
        a = self._assign()
        a.action_lost()
        self.assertEqual(a.state, "lost")

    def test_03_invalid_transitions(self):
        a = self._assign()
        a.action_return()
        with self.assertRaises(UserError):
            a.action_lost()

    def test_04_date_validation(self):
        today = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self.env["phone.assignment"].create({
                "item_id": self.item.id,
                "employee_id": self.employee.id,
                "date_issue": today,
                "date_return": today.replace(year=today.year - 1),
                "company_id": self.env.company.id,
            })

    def test_05_access_control(self):
        a = self._assign()
        with self.assertRaises(Exception):
            self.env["phone.assignment"].with_user(self.outsider).create({
                "item_id": self.item.id,
                "employee_id": self.employee.id,
                "company_id": self.env.company.id,
            })
        a.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Phone B"})
        item_b = self.env["phone.item"].create({"name": "PH-B", "company_id": company_b.id})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["phone.assignment"].create({
            "item_id": item_b.id,
            "employee_id": emp_b.id,
            "company_id": company_b.id,
        })
        visible = self.env["phone.assignment"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
