# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFuelLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vehicle = cls.env["fuel.vehicle"].create({
            "name": "Van 01",
            "ref": "AA-123-AA",
            "company_id": cls.env.company.id,
        })
        cls.employee = cls.env["hr.employee"].create({"name": "Fuel Driver"})
        cls.manager = cls._user(
            "fuellog-manager", ["fs_fleet_fuel_log.group_fsfleetfuell_user"])
        cls.outsider = cls._user(
            "fuellog-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _log(self, liter=40.0, amount=80.0):
        return self.env["fuel.log"].create({
            "vehicle_id": self.vehicle.id,
            "driver_id": self.employee.id,
            "liter": liter,
            "amount_total": amount,
            "company_id": self.env.company.id,
        })

    def test_01_create_and_confirm(self):
        log = self._log()
        self.assertEqual(log.state, "draft")
        self.assertAlmostEqual(log.price_per_liter, 2.0)
        log.action_confirm()
        self.assertEqual(log.state, "confirmed")

    def test_02_reset_confirmed(self):
        log = self._log()
        log.action_confirm()
        log.action_reset()
        self.assertEqual(log.state, "draft")

    def test_03_invalid_values(self):
        with self.assertRaises(ValidationError):
            self._log(liter=0.0)
        with self.assertRaises(ValidationError):
            self._log(amount=-1.0)

    def test_04_cannot_confirm_twice_flow(self):
        log = self._log()
        log.action_confirm()
        with self.assertRaises(UserError):
            log.action_confirm()

    def test_05_access_control(self):
        log = self._log()
        with self.assertRaises(Exception):
            self.env["fuel.log"].with_user(self.outsider).create({
                "vehicle_id": self.vehicle.id,
                "liter": 10.0,
                "amount_total": 20.0,
                "company_id": self.env.company.id,
            })
        log.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Fuel B"})
        veh_b = self.env["fuel.vehicle"].create({
            "name": "Van B", "company_id": company_b.id})
        foreign = self.env["fuel.log"].create({
            "vehicle_id": veh_b.id,
            "liter": 30.0,
            "amount_total": 60.0,
            "company_id": company_b.id,
        })
        visible = self.env["fuel.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
