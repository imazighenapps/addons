# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDriverHoursLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = cls.env["hr.employee"].create({"name": "Truck Driver"})
        cls.manager = cls._user(
            "dhl-manager",
            ["driver_hours_log.group_driverhoursl_user"])
        cls.outsider = cls._user("dhl-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _record(self, **vals):
        data = {
            "name": vals.pop("name", "DHL-TEST"),
            "employee_id": self.driver.id,
            "vehicle_plate": "TR-TEST",
            "duty_date": self.today,
            "driving_minutes": 480,
            "break_minutes": 45,
            "limit_minutes": 540,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["driver.hours.log"].create(data)

    def test_01_create_record(self):
        rec = self._record()
        self.assertEqual(rec.state, "draft")
        self.assertFalse(rec.exceeds_limit)
        self.assertTrue(rec.name)

    def test_02_exceedance_is_computed(self):
        rec = self._record(driving_minutes=570)
        self.assertTrue(rec.exceeds_limit)

    def test_03_validate_within_limit(self):
        rec = self._record()
        rec.action_validate()
        self.assertEqual(rec.state, "validated")

    def test_04_validate_above_limit(self):
        rec = self._record(driving_minutes=570)
        rec.action_validate()
        self.assertEqual(rec.state, "alert")
        rec.action_resolve()
        self.assertEqual(rec.state, "validated")

    def test_05_invalid_transitions(self):
        rec = self._record()
        with self.assertRaises(UserError):
            rec.action_resolve()
        rec.action_validate()
        with self.assertRaises(UserError):
            rec.action_validate()

    def test_06_constraints(self):
        with self.assertRaises(ValidationError):
            self._record(driving_minutes=0)
        with self.assertRaises(ValidationError):
            self._record(driving_minutes=1500)
        with self.assertRaises(ValidationError):
            self._record(break_minutes=-1)

    def test_07_cancel_and_reset(self):
        rec = self._record()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_08_access_control(self):
        with self.assertRaises(Exception):
            self.env["driver.hours.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "employee_id": self.driver.id,
                    "driving_minutes": 60,
                    "company_id": self.env.company.id,
                })
        rec = self._record(name="DHL-ACC")
        rec.with_user(self.manager).read()

    def test_09_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "DHL B"})
        foreign = self.env["driver.hours.log"].create({
            "name": "DHL-FOREIGN",
            "employee_id": self.driver.id,
            "driving_minutes": 60,
            "company_id": company_b.id,
        })
        visible = self.env["driver.hours.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
