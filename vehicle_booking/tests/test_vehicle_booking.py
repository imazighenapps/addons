# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVehicleBooking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vehicle = cls.env["booking.vehicle"].create({
            "name": "Car 1", "plate": "AA-001", "company_id": cls.env.company.id,
        })
        cls.manager = cls._user(
            "vehiclebook-manager", ["vehicle_booking.group_vehiclebooki_user"])
        cls.outsider = cls._user(
            "vehiclebook-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _booking(self, start, stop, state="draft"):
        return self.env["vehicle.booking"].create({
            "name": "Trip",
            "vehicle_id": self.vehicle.id,
            "start_datetime": start,
            "stop_datetime": stop,
            "state": state,
            "company_id": self.env.company.id,
        })

    def test_01_flow_confirm_done(self):
        now = fields.Datetime.now()
        b = self._booking(now, now + timedelta(hours=2))
        b.action_confirm()
        self.assertEqual(b.state, "confirmed")
        b.action_done()
        self.assertEqual(b.state, "done")

    def test_02_overlap_blocked(self):
        now = fields.Datetime.now()
        b1 = self._booking(now, now + timedelta(hours=2), state="confirmed")
        b2 = self._booking(now + timedelta(hours=1), now + timedelta(hours=3))
        with self.assertRaises(ValidationError):
            b2.action_confirm()

    def test_03_end_after_start(self):
        now = fields.Datetime.now()
        with self.assertRaises(ValidationError):
            self._booking(now, now - timedelta(hours=1))

    def test_04_cancel_reset(self):
        now = fields.Datetime.now()
        b = self._booking(now, now + timedelta(hours=1))
        b.action_cancel()
        self.assertEqual(b.state, "cancelled")
        b.action_reset()
        self.assertEqual(b.state, "draft")

    def test_05_access_control(self):
        now = fields.Datetime.now()
        b = self._booking(now, now + timedelta(hours=1))
        with self.assertRaises(Exception):
            self.env["vehicle.booking"].with_user(self.outsider).create({
                "name": "No",
                "vehicle_id": self.vehicle.id,
                "start_datetime": now + timedelta(hours=3),
                "stop_datetime": now + timedelta(hours=4),
                "company_id": self.env.company.id,
            })
        b.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Veh B"})
        veh_b = self.env["booking.vehicle"].create({"name": "Car B", "company_id": company_b.id})
        now = fields.Datetime.now()
        foreign = self.env["vehicle.booking"].create({
            "name": "Foreign",
            "vehicle_id": veh_b.id,
            "start_datetime": now,
            "stop_datetime": now + timedelta(hours=1),
            "company_id": company_b.id,
        })
        visible = self.env["vehicle.booking"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
