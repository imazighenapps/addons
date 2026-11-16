# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFleetTireLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.technician = cls.env["hr.employee"].create({"name": "Tire Technician"})
        cls.manager = cls._user(
            "ftl-manager",
            ["fleet_tire_log.group_fleettirelog_user"])
        cls.outsider = cls._user("ftl-outsider", ["base.group_user"])
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
            "name": vals.pop("name", "FTL-TEST"),
            "vehicle_plate": "TR-TEST",
            "tire_brand": "Test Brand",
            "position": "fl",
            "event_type": "rotation",
            "event_date": self.today,
            "tread_depth_mm": 7.0,
            "odometer": 10000,
            "technician_id": self.technician.id,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["fleet.tire.log"].create(data)

    def test_01_create_event(self):
        rec = self._record()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.name)

    def test_02_record_and_due(self):
        rec = self._record()
        rec.action_record()
        self.assertEqual(rec.state, "recorded")
        rec.action_mark_due()
        self.assertEqual(rec.state, "due")

    def test_03_invalid_transitions(self):
        rec = self._record()
        with self.assertRaises(UserError):
            rec.action_mark_due()
        rec.action_record()
        with self.assertRaises(UserError):
            rec.action_record()

    def test_04_constraints(self):
        with self.assertRaises(ValidationError):
            self._record(tread_depth_mm=-0.5)
        with self.assertRaises(ValidationError):
            self._record(tread_depth_mm=30.0)
        with self.assertRaises(ValidationError):
            self._record(odometer=-1)
        with self.assertRaises(ValidationError):
            self._record(unit_cost=-1.0)

    def test_05_cancel_and_reset(self):
        rec = self._record()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["fleet.tire.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "vehicle_plate": "NO",
                    "company_id": self.env.company.id,
                })
        rec = self._record(name="FTL-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "FTL B"})
        foreign = self.env["fleet.tire.log"].create({
            "name": "FTL-FOREIGN",
            "vehicle_plate": "TR-B",
            "event_date": self.today,
            "company_id": company_b.id,
        })
        visible = self.env["fleet.tire.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
