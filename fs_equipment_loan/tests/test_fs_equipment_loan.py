# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged
from odoo import fields
from datetime import timedelta


@tagged("post_install", "-at_install")
class TestEquipmentLoan(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Loan Test Employee"})
        cls.item = cls.env["equipment.loan.item"].create({
            "name": "Laptop A",
            "ref": "LPT-001",
            "company_id": cls.env.company.id,
        })
        cls.manager = cls._user(
            "equiploan-manager", ["fs_equipment_loan.group_fsequipmentl_user"])
        cls.outsider = cls._user(
            "equiploan-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login,
            "login": login,
            field: [(6, 0, groups)],
        })

    def _loan(self, due=None):
        vals = {
            "item_id": self.item.id,
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
        }
        if due:
            vals["date_due"] = due
        return self.env["equipment.loan"].create(vals)

    def test_01_start_and_return(self):
        loan = self._loan()
        loan.action_start()
        self.assertEqual(loan.state, "ongoing")
        self.assertTrue(self.item.is_on_loan)
        loan.return_condition = "good"
        loan.action_return()
        self.assertEqual(loan.state, "returned")
        self.assertTrue(loan.date_return)
        self.assertEqual(loan.return_condition, "good")

    def test_02_cannot_double_loan(self):
        loan1 = self._loan()
        loan1.action_start()
        loan2 = self._loan()
        with self.assertRaises(ValidationError):
            loan2.action_start()

    def test_03_overdue_flag(self):
        today = fields.Date.context_today(self.env.user)
        past = fields.Date.subtract(today, days=5)
        out = fields.Date.subtract(today, days=10)
        loan = self.env["equipment.loan"].create({
            "item_id": self.item.id,
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
            "date_out": out,
            "date_due": past,
        })
        loan.action_start()
        self.assertTrue(loan.is_overdue)

    def test_04_access_control(self):
        loan = self._loan()
        with self.assertRaises(Exception):
            self.env["equipment.loan"].with_user(self.outsider).create({
                "item_id": self.item.id,
                "employee_id": self.employee.id,
                "company_id": self.env.company.id,
            })
        loan.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Loan B"})
        emp_b = self.env["hr.employee"].create({
            "name": "Emp B", "company_id": company_b.id})
        item_b = self.env["equipment.loan.item"].create({
            "name": "Laptop B", "company_id": company_b.id})
        foreign = self.env["equipment.loan"].create({
            "item_id": item_b.id,
            "employee_id": emp_b.id,
            "company_id": company_b.id,
        })
        visible = self.env["equipment.loan"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
