# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFuelCardAssignment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.card = cls.env["fuel.card"].create({
            "name": "FC-001", "provider": "FuelCo", "company_id": cls.env.company.id,
        })
        cls.employee = cls.env["hr.employee"].create({"name": "Fuel Employee"})
        cls.manager = cls._user(
            "fuelcard-manager", ["fuel_card_assignment.group_fuelcardassi_user"])
        cls.outsider = cls._user(
            "fuelcard-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _assign(self):
        return self.env["fuel.card.assignment"].create({
            "card_id": self.card.id,
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
        })

    def test_01_assign_return(self):
        a = self._assign()
        a.action_return()
        self.assertEqual(a.state, "returned")
        self.assertTrue(a.date_return)

    def test_02_block(self):
        a = self._assign()
        a.action_block()
        self.assertEqual(a.state, "blocked")

    def test_03_invalid_transitions(self):
        a = self._assign()
        a.action_return()
        with self.assertRaises(UserError):
            a.action_block()

    def test_04_date_validation(self):
        today = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self.env["fuel.card.assignment"].create({
                "card_id": self.card.id,
                "employee_id": self.employee.id,
                "date_issue": today,
                "date_return": today.replace(year=today.year - 1),
                "company_id": self.env.company.id,
            })

    def test_05_access_control(self):
        a = self._assign()
        with self.assertRaises(Exception):
            self.env["fuel.card.assignment"].with_user(self.outsider).create({
                "card_id": self.card.id,
                "employee_id": self.employee.id,
                "company_id": self.env.company.id,
            })
        a.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Fuel B"})
        card_b = self.env["fuel.card"].create({"name": "FC-B", "company_id": company_b.id})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["fuel.card.assignment"].create({
            "card_id": card_b.id,
            "employee_id": emp_b.id,
            "company_id": company_b.id,
        })
        visible = self.env["fuel.card.assignment"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
