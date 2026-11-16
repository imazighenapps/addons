# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEmergencyLightLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tester = cls.env["hr.employee"].create({"name": "Lighting Tester"})
        cls.manager = cls._user(
            "ell-manager",
            ["emergency_light_log.group_emergencylig_user"])
        cls.outsider = cls._user("ell-outsider", ["base.group_user"])
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
            "name": vals.pop("name", "ELL-TEST"),
            "light_ref": "LGT-TEST",
            "location": "Test Site",
            "light_type": "non_maintained",
            "test_date": self.today,
            "next_test_date": self.today + timedelta(days=30),
            "tester_id": self.tester.id,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["emergency.light.log"].create(data)

    def test_01_create_test(self):
        rec = self._record()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.name)

    def test_02_validate_test(self):
        rec = self._record()
        rec.action_test()
        self.assertEqual(rec.state, "tested")

    def test_03_validate_requires_flags(self):
        rec = self._record(lamp_ok=False)
        with self.assertRaises(UserError):
            rec.action_test()
        self.assertEqual(rec.state, "draft")

    def test_04_mark_failed(self):
        rec = self._record(battery_ok=False)
        rec.action_fail()
        self.assertEqual(rec.state, "failed")

    def test_05_invalid_transitions(self):
        rec = self._record()
        rec.action_test()
        with self.assertRaises(UserError):
            rec.action_test()
        with self.assertRaises(UserError):
            rec.action_fail()

    def test_06_constraints(self):
        with self.assertRaises(ValidationError):
            self._record(duration_minutes=-1)
        with self.assertRaises(ValidationError):
            self._record(next_test_date=self.today - timedelta(days=1))

    def test_07_cancel_and_reset(self):
        rec = self._record()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_08_access_control(self):
        with self.assertRaises(Exception):
            self.env["emergency.light.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "light_ref": "NO",
                    "location": "No",
                    "company_id": self.env.company.id,
                })
        rec = self._record(name="ELL-ACC")
        rec.with_user(self.manager).read()

    def test_09_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "ELL B"})
        foreign = self.env["emergency.light.log"].create({
            "name": "ELL-FOREIGN",
            "light_ref": "LGT-B",
            "location": "Foreign",
            "test_date": self.today,
            "next_test_date": self.today + timedelta(days=30),
            "company_id": company_b.id,
        })
        visible = self.env["emergency.light.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
