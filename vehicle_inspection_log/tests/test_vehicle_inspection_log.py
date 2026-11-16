# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVehicleInspectionLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspector = cls.env["hr.employee"].create({"name": "Fleet Inspector"})
        cls.manager = cls._user(
            "vil-manager",
            ["vehicle_inspection_log.group_vehicleinspe_user"])
        cls.outsider = cls._user("vil-outsider", ["base.group_user"])
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
            "name": vals.pop("name", "VIL-TEST"),
            "vehicle_plate": "TR-TEST",
            "vehicle_model": "Test Model",
            "inspection_date": self.today,
            "odometer": 10000,
            "inspector_id": self.inspector.id,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["vehicle.inspection.log"].create(data)

    def test_01_create_inspection(self):
        rec = self._record()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.name)

    def test_02_pass_inspection(self):
        rec = self._record()
        rec.action_pass()
        self.assertEqual(rec.state, "passed")

    def test_03_pass_requires_checks(self):
        rec = self._record(brake_ok=False)
        with self.assertRaises(UserError):
            rec.action_pass()
        self.assertEqual(rec.state, "draft")

    def test_04_flag_defect(self):
        rec = self._record(light_ok=False)
        rec.action_flag_defect()
        self.assertEqual(rec.state, "defect")

    def test_05_invalid_transitions(self):
        rec = self._record()
        rec.action_pass()
        with self.assertRaises(UserError):
            rec.action_pass()
        with self.assertRaises(UserError):
            rec.action_flag_defect()

    def test_06_odometer_constraint(self):
        with self.assertRaises(ValidationError):
            self._record(odometer=-1)

    def test_07_cancel_and_reset(self):
        rec = self._record()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_08_access_control(self):
        with self.assertRaises(Exception):
            self.env["vehicle.inspection.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "vehicle_plate": "NO",
                    "company_id": self.env.company.id,
                })
        rec = self._record(name="VIL-ACC")
        rec.with_user(self.manager).read()

    def test_09_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "VIL B"})
        foreign = self.env["vehicle.inspection.log"].create({
            "name": "VIL-FOREIGN",
            "vehicle_plate": "TR-B",
            "inspection_date": self.today,
            "company_id": company_b.id,
        })
        visible = self.env["vehicle.inspection.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
