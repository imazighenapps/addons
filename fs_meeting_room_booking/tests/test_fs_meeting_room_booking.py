# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMeetingRoomBooking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.room = cls.env["meeting.room"].create({
            "name": "Room A",
            "capacity": 8,
            "company_id": cls.env.company.id,
        })
        cls.manager = cls._user(
            "roombook-manager", ["fs_meeting_room_booking.group_fsmeetingroo_user"])
        cls.outsider = cls._user(
            "roombook-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _booking(self, start, stop, state="draft"):
        return self.env["meeting.booking"].create({
            "name": "Meeting",
            "room_id": self.room.id,
            "start_datetime": start,
            "stop_datetime": stop,
            "state": state,
            "company_id": self.env.company.id,
        })

    def test_01_confirm_booking(self):
        now = fields.Datetime.now()
        b = self._booking(now, now + timedelta(hours=1))
        b.action_confirm()
        self.assertEqual(b.state, "confirmed")

    def test_02_overlap_blocked(self):
        now = fields.Datetime.now()
        b1 = self._booking(now, now + timedelta(hours=1), state="confirmed")
        b2 = self._booking(now + timedelta(minutes=30), now + timedelta(hours=2))
        with self.assertRaises(ValidationError):
            b2.action_confirm()

    def test_03_end_after_start(self):
        now = fields.Datetime.now()
        with self.assertRaises(ValidationError):
            self._booking(now, now - timedelta(hours=1))

    def test_04_cancel_and_reset(self):
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
            self.env["meeting.booking"].with_user(self.outsider).create({
                "name": "No",
                "room_id": self.room.id,
                "start_datetime": now + timedelta(hours=2),
                "stop_datetime": now + timedelta(hours=3),
                "company_id": self.env.company.id,
            })
        b.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Room B"})
        room_b = self.env["meeting.room"].create({
            "name": "Room B1", "company_id": company_b.id})
        now = fields.Datetime.now()
        foreign = self.env["meeting.booking"].create({
            "name": "Foreign",
            "room_id": room_b.id,
            "start_datetime": now,
            "stop_datetime": now + timedelta(hours=1),
            "company_id": company_b.id,
        })
        visible = self.env["meeting.booking"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
