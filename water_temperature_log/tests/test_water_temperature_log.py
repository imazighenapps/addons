# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWaterTemperatureLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reader = cls.env["hr.employee"].create({"name": "Water Reader"})
        cls.manager = cls._user(
            "wtl-manager",
            ["water_temperature_log.group_watertempera_user"])
        cls.outsider = cls._user("wtl-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _reading(self, **vals):
        data = {
            "name": vals.pop("name", "WTL-TEST"),
            "point_name": "Test Tap",
            "point_type": "tap",
            "reading_date": self.today,
            "temperature_c": 55.0,
            "target_min_c": 50.0,
            "target_max_c": 65.0,
            "reader_id": self.reader.id,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["water.temperature.log"].create(data)

    def test_01_create_reading(self):
        rec = self._reading()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.within_range)
        self.assertTrue(rec.name)

    def test_02_out_of_range_is_flagged(self):
        rec = self._reading(temperature_c=43.0)
        self.assertFalse(rec.within_range)

    def test_03_record_in_range(self):
        rec = self._reading()
        rec.action_record()
        self.assertEqual(rec.state, "recorded")

    def test_04_record_out_of_range(self):
        rec = self._reading(temperature_c=43.0)
        rec.action_record()
        self.assertEqual(rec.state, "alert")
        rec.action_resolve()
        self.assertEqual(rec.state, "recorded")

    def test_05_invalid_transitions(self):
        rec = self._reading()
        with self.assertRaises(UserError):
            rec.action_resolve()
        rec.action_record()
        with self.assertRaises(UserError):
            rec.action_record()

    def test_06_constraints(self):
        with self.assertRaises(ValidationError):
            self._reading(temperature_c=121.0)
        with self.assertRaises(ValidationError):
            self._reading(target_min_c=70.0, target_max_c=60.0)

    def test_07_cancel_and_reset(self):
        rec = self._reading()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_08_access_control(self):
        with self.assertRaises(Exception):
            self.env["water.temperature.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "point_name": "No",
                    "temperature_c": 55.0,
                    "company_id": self.env.company.id,
                })
        rec = self._reading(name="WTL-ACC")
        rec.with_user(self.manager).read()

    def test_09_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "WTL B"})
        foreign = self.env["water.temperature.log"].create({
            "name": "WTL-FOREIGN",
            "point_name": "Foreign Tap",
            "temperature_c": 55.0,
            "company_id": company_b.id,
        })
        visible = self.env["water.temperature.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
