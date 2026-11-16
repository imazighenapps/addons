# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCoolerTemperatureLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reader = cls.env["hr.employee"].create({"name": "Cold Store Reader"})
        cls.manager = cls._user(
            "ctl-manager",
            ["cooler_temperature_log.group_coolertemper_user"])
        cls.outsider = cls._user("ctl-outsider", ["base.group_user"])
        cls.now = fields.Datetime.now()

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _reading(self, **vals):
        data = {
            "name": vals.pop("name", "CTL-TEST"),
            "cooler_name": "Test Cooler",
            "location": "Test Store",
            "reading_date": self.now,
            "temperature_c": 3.0,
            "target_min_c": 0.0,
            "target_max_c": 4.0,
            "reader_id": self.reader.id,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["cooler.temperature.log"].create(data)

    def test_01_create_reading(self):
        rec = self._reading()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.within_range)
        self.assertTrue(rec.name)

    def test_02_out_of_range_is_flagged(self):
        rec = self._reading(temperature_c=7.5)
        self.assertFalse(rec.within_range)

    def test_03_record_in_range(self):
        rec = self._reading()
        rec.action_record()
        self.assertEqual(rec.state, "recorded")

    def test_04_record_breach(self):
        rec = self._reading(temperature_c=7.5)
        rec.action_record()
        self.assertEqual(rec.state, "breach")
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
            self._reading(temperature_c=41.0)
        with self.assertRaises(ValidationError):
            self._reading(target_min_c=5.0, target_max_c=4.0)

    def test_07_cancel_and_reset(self):
        rec = self._reading()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_08_access_control(self):
        with self.assertRaises(Exception):
            self.env["cooler.temperature.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "cooler_name": "No",
                    "temperature_c": 3.0,
                    "company_id": self.env.company.id,
                })
        rec = self._reading(name="CTL-ACC")
        rec.with_user(self.manager).read()

    def test_09_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "CTL B"})
        foreign = self.env["cooler.temperature.log"].create({
            "name": "CTL-FOREIGN",
            "cooler_name": "Foreign Cooler",
            "temperature_c": 3.0,
            "company_id": company_b.id,
        })
        visible = self.env["cooler.temperature.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
