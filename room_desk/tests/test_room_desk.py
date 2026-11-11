# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRoomBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "RoomBook Other Company",
        })
        cls.room = cls.env["room.room"].create({
            "name": "RoomBook Test Atlas",
            "code": "RB-A1",
            "location": "Floor 1",
            "capacity": 8,
            "equipment": "Projector",
        })
        cls.room_b = cls.env["room.room"].create({
            "name": "RoomBook Test Boreal",
            "code": "RB-B1",
            "location": "Floor 2",
            "capacity": 4,
        })

    def _booking(self, room=None, **values):
        defaults = {
            "name": "RoomBook Test Meeting",
            "room_id": (room or self.room).id,
            "host_id": self.env.user.id,
            "start_at": datetime(2026, 11, 10, 9, 0, 0),
            "end_at": datetime(2026, 11, 10, 10, 0, 0),
            "attendee_count": 3,
        }
        defaults.update(values)
        return self.env["room.booking"].create(defaults)

    def test_01_booking_defaults(self):
        booking = self._booking()
        self.assertEqual(booking.state, "draft")
        self.assertEqual(booking.company_id, self.env.company)
        self.assertEqual(booking.attendee_count, 3)
        self.assertEqual(booking.host_id, self.env.user)

    def test_02_confirm_and_cancel(self):
        booking = self._booking()
        self.assertTrue(booking.action_confirm())
        self.assertEqual(booking.state, "confirmed")
        self.assertTrue(booking.action_cancel())
        self.assertEqual(booking.state, "cancelled")
        self.assertTrue(booking.action_reset())
        self.assertEqual(booking.state, "draft")

    def test_03_confirm_requires_draft(self):
        booking = self._booking()
        booking.action_confirm()
        with self.assertRaises(UserError):
            booking.action_confirm()
        booking.action_cancel()
        with self.assertRaises(UserError):
            booking.action_cancel()

    def test_04_end_before_start_is_refused(self):
        with self.assertRaises(ValidationError):
            self._booking(start_at=datetime(2026, 11, 10, 10, 0, 0),
                          end_at=datetime(2026, 11, 10, 9, 0, 0))
        with self.assertRaises(ValidationError):
            self._booking(start_at=datetime(2026, 11, 10, 10, 0, 0),
                          end_at=datetime(2026, 11, 10, 10, 0, 0))

    def test_05_attendee_count_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._booking(attendee_count=0)
        with self.assertRaises(ValidationError):
            self._booking(attendee_count=-1)

    def test_06_overlap_is_blocked_for_confirmed(self):
        first = self._booking(name="RoomBook Test Alpha")
        first.action_confirm()
        second = self._booking(
            name="RoomBook Test Beta",
            start_at=datetime(2026, 11, 10, 9, 30, 0),
            end_at=datetime(2026, 11, 10, 10, 30, 0),
        )
        with self.assertRaises(ValidationError):
            second.action_confirm()
        second.write({"room_id": self.room_b.id})
        self.assertTrue(second.action_confirm())
        third = self._booking(
            name="RoomBook Test Gamma",
            start_at=datetime(2026, 11, 10, 10, 0, 0),
            end_at=datetime(2026, 11, 10, 11, 0, 0),
        )
        self.assertTrue(third.action_confirm())

    def test_07_cancelled_bookings_do_not_block(self):
        first = self._booking(name="RoomBook Test Cancelled")
        first.action_confirm()
        first.action_cancel()
        second = self._booking(
            name="RoomBook Test Reuse",
            start_at=datetime(2026, 11, 10, 9, 15, 0),
            end_at=datetime(2026, 11, 10, 9, 45, 0),
        )
        self.assertTrue(second.action_confirm())
        self.assertEqual(second.state, "confirmed")

    def test_08_room_counters(self):
        confirmed = self._booking(name="RoomBook Test Count 1",
                                  start_at=datetime(2027, 1, 5, 8, 0, 0),
                                  end_at=datetime(2027, 1, 5, 9, 0, 0))
        confirmed.action_confirm()
        draft = self._booking(name="RoomBook Test Count 2",
                              start_at=datetime(2027, 1, 5, 10, 0, 0),
                              end_at=datetime(2027, 1, 5, 11, 0, 0))
        self.room.invalidate_recordset()
        self.assertEqual(self.room.booking_count, 2)
        self.assertGreaterEqual(self.room.upcoming_count, 1)
        self.assertEqual(draft.state, "draft")

    def test_09_company_isolation(self):
        foreign_room = self.env["room.room"].with_company(
            self.other_company).sudo().create({
            "name": "RoomBook Test Foreign Room",
            "capacity": 6,
            "company_id": self.other_company.id,
        })
        foreign = self.env["room.booking"].with_company(
            self.other_company).sudo().create({
            "name": "RoomBook Test Foreign Booking",
            "room_id": foreign_room.id,
            "host_id": self.env.user.id,
            "start_at": datetime(2026, 12, 1, 14, 0, 0),
            "end_at": datetime(2026, 12, 1, 15, 0, 0),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._booking(name="RoomBook Test Local")
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
