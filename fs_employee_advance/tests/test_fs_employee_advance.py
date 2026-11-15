# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEmployeeAdvance(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Advance Test Employee"})
        cls.manager = cls._user(
            "advance-manager", ["fs_employee_advance.group_fsemployeead_user"])
        cls.outsider = cls._user(
            "advance-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login,
            "login": login,
            field: [(6, 0, groups)],
        })

    def _advance(self, amount=200.0):
        return self.env["employee.advance"].create({
            "employee_id": self.employee.id,
            "amount_requested": amount,
            "purpose": "Travel",
            "company_id": self.env.company.id,
        })

    def test_01_flow_partial_and_clear(self):
        adv = self._advance(200.0)
        adv.action_approve()
        self.assertEqual(adv.state, "approved")
        adv.action_pay()
        self.assertEqual(adv.state, "paid")
        self.assertAlmostEqual(adv.amount_outstanding, 200.0)
        self.env["employee.advance.clearing"].create({
            "advance_id": adv.id,
            "amount": 80.0,
            "clearing_type": "expense",
        })
        self.assertEqual(adv.state, "partial")
        self.assertAlmostEqual(adv.amount_outstanding, 120.0)
        self.env["employee.advance.clearing"].create({
            "advance_id": adv.id,
            "amount": 120.0,
            "clearing_type": "return",
        })
        self.assertEqual(adv.state, "cleared")
        self.assertAlmostEqual(adv.amount_outstanding, 0.0)

    def test_02_cannot_clear_beyond_paid(self):
        adv = self._advance(100.0)
        adv.action_approve()
        adv.action_pay()
        with self.assertRaises(ValidationError):
            self.env["employee.advance.clearing"].create({
                "advance_id": adv.id,
                "amount": 150.0,
                "clearing_type": "expense",
            })

    def test_03_cannot_cancel_paid(self):
        adv = self._advance(100.0)
        adv.action_approve()
        adv.action_pay()
        with self.assertRaises(UserError):
            adv.action_cancel()

    def test_04_access_control(self):
        adv = self._advance(50.0)
        with self.assertRaises(Exception):
            self.env["employee.advance"].with_user(self.outsider).create({
                "employee_id": self.employee.id,
                "amount_requested": 10.0,
                "company_id": self.env.company.id,
            })
        adv.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Advance B"})
        emp_b = self.env["hr.employee"].create({
            "name": "Emp B", "company_id": company_b.id})
        foreign = self.env["employee.advance"].create({
            "employee_id": emp_b.id,
            "amount_requested": 75.0,
            "company_id": company_b.id,
        })
        visible = self.env["employee.advance"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
