# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestUniformAllocation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.item = cls.env["uniform.item"].create({
            "name": "Safety Vest", "item_type": "ppe", "company_id": cls.env.company.id,
        })
        cls.employee = cls.env["hr.employee"].create({"name": "Uniform Employee"})
        cls.manager = cls._user(
            "uniform-manager", ["uniform_allocation.group_uniformalloc_user"])
        cls.outsider = cls._user(
            "uniform-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _alloc(self):
        return self.env["uniform.allocation"].create({
            "employee_id": self.employee.id,
            "item_id": self.item.id,
            "quantity": 2.0,
            "size": "L",
            "company_id": self.env.company.id,
        })

    def test_01_issue_return(self):
        a = self._alloc()
        self.assertEqual(a.state, "issued")
        a.action_return()
        self.assertEqual(a.state, "returned")
        self.assertTrue(a.date_return)

    def test_02_replace(self):
        a = self._alloc()
        a.action_replace()
        self.assertEqual(a.state, "replaced")

    def test_03_invalid_transitions(self):
        a = self._alloc()
        a.action_return()
        with self.assertRaises(UserError):
            a.action_replace()

    def test_04_quantity_validation(self):
        with self.assertRaises(ValidationError):
            self.env["uniform.allocation"].create({
                "employee_id": self.employee.id,
                "item_id": self.item.id,
                "quantity": 0.0,
                "company_id": self.env.company.id,
            })

    def test_05_access_control(self):
        a = self._alloc()
        with self.assertRaises(Exception):
            self.env["uniform.allocation"].with_user(self.outsider).create({
                "employee_id": self.employee.id,
                "item_id": self.item.id,
                "quantity": 1.0,
                "company_id": self.env.company.id,
            })
        a.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Uniform B"})
        item_b = self.env["uniform.item"].create({"name": "Vest B", "company_id": company_b.id})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["uniform.allocation"].create({
            "employee_id": emp_b.id,
            "item_id": item_b.id,
            "quantity": 1.0,
            "company_id": company_b.id,
        })
        visible = self.env["uniform.allocation"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
