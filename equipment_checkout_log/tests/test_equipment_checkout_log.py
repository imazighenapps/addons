# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEquipmentCheckoutLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env["maintenance.equipment"].create({
            "name": "Test Equipment",
        })
        cls.employee = cls.env["hr.employee"].create({"name": "Borrower"})
        cls.manager = cls._user(
            "ecl-manager",
            ["equipment_checkout_log.group_equipmentche_user"])
        cls.outsider = cls._user("ecl-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _checkout(self, **vals):
        data = {
            "name": vals.pop("name", "ECL-TEST"),
            "equipment_id": self.equipment.id,
            "employee_id": self.employee.id,
            "checkout_date": self.today,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["equipment.checkout.log"].create(data)

    def test_01_create_checkout(self):
        rec = self._checkout()
        self.assertEqual(rec.state, "draft")

    def test_02_checkout_and_return(self):
        rec = self._checkout()
        rec.action_checkout()
        self.assertEqual(rec.state, "out")
        rec.action_return()
        self.assertEqual(rec.state, "returned")
        self.assertTrue(rec.return_date)

    def test_03_cancel_and_reset(self):
        rec = self._checkout()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._checkout()
        with self.assertRaises(UserError):
            rec.action_return()
        rec.action_checkout()
        rec.action_return()
        with self.assertRaises(UserError):
            rec.action_cancel()

    def test_05_date_validation(self):
        with self.assertRaises(ValidationError):
            self._checkout(
                checkout_date=self.today,
                expected_return_date=self.today - timedelta(days=1),
            )

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["equipment.checkout.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "equipment_id": self.equipment.id,
                    "employee_id": self.employee.id,
                    "company_id": self.env.company.id,
                })
        rec = self._checkout(name="ECL-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "ECL B"})
        foreign = self.env["equipment.checkout.log"].create({
            "name": "ECL-FOREIGN",
            "equipment_id": self.equipment.id,
            "employee_id": self.employee.id,
            "company_id": company_b.id,
        })
        visible = self.env["equipment.checkout.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
