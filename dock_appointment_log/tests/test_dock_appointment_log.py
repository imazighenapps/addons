# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDockAppointmentLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "dal-manager",
            ["dock_appointment_log.group_dockappointm_user"])
        cls.outsider = cls._user("dal-outsider", ["base.group_user"])
        cls.now = fields.Datetime.now()

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _appointment(self, **vals):
        data = {
            "name": vals.pop("name", "DAL-TEST"),
            "appointment_date": self.now + timedelta(days=1),
            "dock_name": "Dock A",
            "direction": "in",
            "carrier_name": "Test Carrier",
            "pallet_count": 4,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["dock.appointment.log"].create(data)

    def test_01_create_appointment(self):
        rec = self._appointment()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.name)

    def test_02_confirm_and_done(self):
        rec = self._appointment()
        rec.action_confirm()
        self.assertEqual(rec.state, "confirmed")
        rec.action_done()
        self.assertEqual(rec.state, "done")

    def test_03_invalid_transitions(self):
        rec = self._appointment()
        with self.assertRaises(UserError):
            rec.action_done()
        rec.action_confirm()
        with self.assertRaises(UserError):
            rec.action_confirm()
        rec.action_done()
        with self.assertRaises(UserError):
            rec.action_cancel()

    def test_04_cancel_and_reset(self):
        rec = self._appointment()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_05_pallet_constraint(self):
        with self.assertRaises(ValidationError):
            self._appointment(pallet_count=-1)

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["dock.appointment.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "appointment_date": self.now,
                    "dock_name": "No",
                    "company_id": self.env.company.id,
                })
        rec = self._appointment(name="DAL-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "DAL B"})
        foreign = self.env["dock.appointment.log"].create({
            "name": "DAL-FOREIGN",
            "appointment_date": self.now,
            "dock_name": "Foreign Dock",
            "company_id": company_b.id,
        })
        visible = self.env["dock.appointment.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
