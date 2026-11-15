# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDriverAssignmentLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Driver A"})
        brand = cls.env["fleet.vehicle.model.brand"].search([], limit=1)
        if not brand:
            brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Brand"})
        model = cls.env["fleet.vehicle.model"].search([], limit=1)
        if not model:
            model = cls.env["fleet.vehicle.model"].create({
                "name": "Model", "brand_id": brand.id,
            })
        cls.vehicle = cls.env["fleet.vehicle"].create({
            "model_id": model.id, "license_plate": "TST-1",
        })
        cls.manager = cls._user(
            "das-manager", ["driver_assignment_log.group_driverassign_user"])
        cls.outsider = cls._user("das-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _rec(self):
        return self.env["driver.assignment.log"].create({
            "vehicle_id": self.vehicle.id,
            "employee_id": self.employee.id,
            "date_start": fields.Date.context_today(self.env.user),
            "company_id": self.env.company.id,
        })

    def test_01_end_assignment(self):
        r = self._rec()
        r.action_end()
        self.assertEqual(r.state, "ended")
        self.assertTrue(r.date_end)

    def test_02_cancel_reactivate(self):
        r = self._rec()
        r.action_cancel()
        self.assertEqual(r.state, "cancelled")
        r.action_reactivate()
        self.assertEqual(r.state, "active")

    def test_03_state_guards(self):
        r = self._rec()
        r.action_end()
        with self.assertRaises(UserError):
            r.action_end()

    def test_04_date_validation(self):
        today = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self.env["driver.assignment.log"].create({
                "vehicle_id": self.vehicle.id,
                "employee_id": self.employee.id,
                "date_start": today,
                "date_end": today - timedelta(days=1),
                "company_id": self.env.company.id,
            })

    def test_05_access_control(self):
        r = self._rec()
        with self.assertRaises(Exception):
            self.env["driver.assignment.log"].with_user(self.outsider).create({
                "vehicle_id": self.vehicle.id,
                "employee_id": self.employee.id,
                "date_start": fields.Date.context_today(self.env.user),
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "DA B"})
        foreign = self.env["driver.assignment.log"].create({
            "vehicle_id": self.vehicle.id,
            "employee_id": self.employee.id,
            "date_start": fields.Date.context_today(self.env.user),
            "company_id": company_b.id,
        })
        visible = self.env["driver.assignment.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
