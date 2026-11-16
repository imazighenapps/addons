# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNoiseExposureLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Noise Operator"})
        cls.manager = cls._user(
            "nel-manager",
            ["noise_exposure_log.group_noiseexposur_user"])
        cls.outsider = cls._user("nel-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _measurement(self, **vals):
        data = {
            "name": vals.pop("name", "NEL-TEST"),
            "location": "Test Workshop",
            "employee_id": self.employee.id,
            "measurement_date": self.today,
            "measured_db": 80.0,
            "limit_db": 85.0,
            "exposure_minutes": 480,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["noise.exposure.log"].create(data)

    def test_01_create_measurement(self):
        rec = self._measurement()
        self.assertEqual(rec.state, "draft")
        self.assertFalse(rec.exceeds_limit)
        self.assertTrue(rec.name)

    def test_02_exceedance_is_computed(self):
        rec = self._measurement(measured_db=92.0)
        self.assertTrue(rec.exceeds_limit)

    def test_03_record_below_limit(self):
        rec = self._measurement()
        rec.action_record()
        self.assertEqual(rec.state, "recorded")

    def test_04_record_above_limit(self):
        rec = self._measurement(measured_db=92.0)
        rec.action_record()
        self.assertEqual(rec.state, "action_required")
        rec.action_resolve()
        self.assertEqual(rec.state, "recorded")

    def test_05_invalid_transitions(self):
        rec = self._measurement()
        with self.assertRaises(UserError):
            rec.action_resolve()
        rec.action_record()
        with self.assertRaises(UserError):
            rec.action_record()

    def test_06_constraints(self):
        with self.assertRaises(ValidationError):
            self._measurement(measured_db=-1.0)
        with self.assertRaises(ValidationError):
            self._measurement(limit_db=0.0)
        with self.assertRaises(ValidationError):
            self._measurement(exposure_minutes=0)

    def test_07_cancel_and_reset(self):
        rec = self._measurement()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_08_access_control(self):
        with self.assertRaises(Exception):
            self.env["noise.exposure.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "location": "No",
                    "measured_db": 80.0,
                    "company_id": self.env.company.id,
                })
        rec = self._measurement(name="NEL-ACC")
        rec.with_user(self.manager).read()

    def test_09_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "NEL B"})
        foreign = self.env["noise.exposure.log"].create({
            "name": "NEL-FOREIGN",
            "location": "Foreign",
            "measured_db": 80.0,
            "company_id": company_b.id,
        })
        visible = self.env["noise.exposure.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
