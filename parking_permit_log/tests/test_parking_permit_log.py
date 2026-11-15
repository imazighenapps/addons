# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestParkingPermitLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Permit Employee"})
        cls.today = fields.Date.context_today(cls.env.user)
        cls.manager = cls._user(
            "ppl-manager",
            ["parking_permit_log.group_parkingpermi_user"])
        cls.outsider = cls._user("ppl-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _permit(self, **vals):
        data = {
            "name": vals.pop("name", "PPL-TEST"),
            "employee_id": self.employee.id,
            "vehicle_plate": "TST-001",
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["parking.permit.log"].create(data)

    def test_01_create_permit(self):
        rec = self._permit()
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.permit_type, "employee")

    def test_02_state_flow(self):
        rec = self._permit()
        rec.action_activate()
        self.assertEqual(rec.state, "active")
        rec.action_expire()
        self.assertEqual(rec.state, "expired")
        rec.action_activate()
        self.assertEqual(rec.state, "active")
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")

    def test_03_reset_draft(self):
        rec = self._permit()
        rec.action_activate()
        rec.action_expire()
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._permit()
        with self.assertRaises(UserError):
            rec.action_expire()
        rec.action_activate()
        with self.assertRaises(UserError):
            rec.action_activate()

    def test_05_end_before_start_is_refused(self):
        with self.assertRaises(ValidationError):
            self._permit(
                date_start=self.today,
                date_end=self.today - timedelta(days=1),
            )

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["parking.permit.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "employee_id": self.employee.id,
                    "company_id": self.env.company.id,
                })
        rec = self._permit(name="PPL-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "PPL B"})
        foreign = self.env["parking.permit.log"].create({
            "name": "PPL-FOREIGN",
            "employee_id": self.employee.id,
            "company_id": company_b.id,
        })
        visible = self.env["parking.permit.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
