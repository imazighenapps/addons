# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestParkingReservation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.spot = cls.env["parking.spot"].create({
            "name": "A-01", "location": "Level 1", "company_id": cls.env.company.id,
        })
        cls.manager = cls._user(
            "parking-manager", ["parking_reservation.group_parkingreser_user"])
        cls.outsider = cls._user(
            "parking-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _res(self, start, stop, state="draft"):
        return self.env["parking.reservation"].create({
            "spot_id": self.spot.id,
            "start_datetime": start,
            "stop_datetime": stop,
            "state": state,
            "company_id": self.env.company.id,
        })

    def test_01_confirm_reservation(self):
        now = fields.Datetime.now()
        r = self._res(now, now + timedelta(hours=2))
        r.action_confirm()
        self.assertEqual(r.state, "confirmed")

    def test_02_overlap_blocked(self):
        now = fields.Datetime.now()
        r1 = self._res(now, now + timedelta(hours=2), state="confirmed")
        r2 = self._res(now + timedelta(hours=1), now + timedelta(hours=3))
        with self.assertRaises(ValidationError):
            r2.action_confirm()

    def test_03_end_after_start(self):
        now = fields.Datetime.now()
        with self.assertRaises(ValidationError):
            self._res(now, now - timedelta(hours=1))

    def test_04_cancel_reset(self):
        now = fields.Datetime.now()
        r = self._res(now, now + timedelta(hours=1))
        r.action_cancel()
        self.assertEqual(r.state, "cancelled")
        r.action_reset()
        self.assertEqual(r.state, "draft")

    def test_05_access_control(self):
        now = fields.Datetime.now()
        r = self._res(now, now + timedelta(hours=1))
        with self.assertRaises(Exception):
            self.env["parking.reservation"].with_user(self.outsider).create({
                "spot_id": self.spot.id,
                "start_datetime": now + timedelta(hours=3),
                "stop_datetime": now + timedelta(hours=4),
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Park B"})
        spot_b = self.env["parking.spot"].create({"name": "B-01", "company_id": company_b.id})
        now = fields.Datetime.now()
        foreign = self.env["parking.reservation"].create({
            "spot_id": spot_b.id,
            "start_datetime": now,
            "stop_datetime": now + timedelta(hours=1),
            "company_id": company_b.id,
        })
        visible = self.env["parking.reservation"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
