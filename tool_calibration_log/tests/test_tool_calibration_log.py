# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestToolCalibrationLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env["maintenance.equipment"].create({
            "name": "Test Tool",
        })
        cls.manager = cls._user(
            "tcl-manager",
            ["tool_calibration_log.group_toolcalibrat_user"])
        cls.outsider = cls._user("tcl-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _cal(self, **vals):
        data = {
            "name": vals.pop("name", "TCL-TEST"),
            "equipment_id": self.equipment.id,
            "calibration_date": self.today,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["tool.calibration.log"].create(data)

    def test_01_create_calibration(self):
        rec = self._cal()
        self.assertEqual(rec.state, "draft")

    def test_02_state_flow(self):
        rec = self._cal()
        rec.action_schedule()
        self.assertEqual(rec.state, "scheduled")
        rec.action_done()
        self.assertEqual(rec.state, "done")

    def test_03_cancel_and_reset(self):
        rec = self._cal()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._cal()
        with self.assertRaises(UserError):
            rec.action_done()
        rec.action_schedule()
        rec.action_done()
        with self.assertRaises(UserError):
            rec.action_cancel()

    def test_05_due_date_validation(self):
        with self.assertRaises(ValidationError):
            self._cal(
                calibration_date=self.today,
                next_due_date=self.today - timedelta(days=1),
            )

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["tool.calibration.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "equipment_id": self.equipment.id,
                    "company_id": self.env.company.id,
                })
        rec = self._cal(name="TCL-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "TCL B"})
        foreign = self.env["tool.calibration.log"].create({
            "name": "TCL-FOREIGN",
            "equipment_id": self.equipment.id,
            "company_id": company_b.id,
        })
        visible = self.env["tool.calibration.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
