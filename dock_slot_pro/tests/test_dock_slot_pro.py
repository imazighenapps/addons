# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDockSlotPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "DockSlotPro Test Customer",
        })
        cls.other_partner = cls.env["res.partner"].create({
            "name": "DockSlotPro Second Customer",
        })
        # 2026-01-05 is a Monday, so it matches the weekday "0" slots.
        cls.monday = date(2026, 1, 5)
        cls.next_monday = date(2026, 1, 12)
        cls.third_monday = date(2026, 1, 19)
        cls.slot = cls.env["dock.slot"].create({
            "name": "Monday morning dock A",
            "weekday": "0",
            "start_hour": 8.0,
            "end_hour": 12.0,
            "capacity": 2,
            "location": "Dock A",
        })
        cls.roomy_slot = cls.env["dock.slot"].create({
            "name": "Monday afternoon dock B",
            "weekday": "0",
            "start_hour": 14.0,
            "end_hour": 18.0,
            "capacity": 5,
            "location": "Dock B",
        })

    def _slot(self, **kwargs):
        values = {
            "name": "Test delivery window",
            "weekday": "0",
            "start_hour": 8.0,
            "end_hour": 12.0,
            "capacity": 2,
        }
        values.update(kwargs)
        return self.env["dock.slot"].create(values)

    def _booking(self, slot=None, day=None, partner=None, **kwargs):
        values = {
            "slot_id": (slot or self.slot).id,
            "date": day or self.monday,
            "partner_id": (partner or self.partner).id,
        }
        values.update(kwargs)
        return self.env["dock.booking"].create(values)

    def test_01_sequence_and_weekday(self):
        first = self._booking()
        second = self._booking(partner=self.other_partner)
        self.assertTrue(first.name.startswith("DCK/"), first.name)
        self.assertNotEqual(first.name, second.name)
        self.assertEqual(first.state, "draft")
        self.assertEqual(first.slot_id.weekday, "0")
        self.assertEqual(first.date.weekday(), int(first.slot_id.weekday))
        self.assertEqual(first.user_id, self.env.user)

    def test_02_wrong_weekday_refused(self):
        tuesday = self.monday + timedelta(days=1)
        with self.assertRaises(ValidationError):
            self._booking(day=tuesday)
        booking = self._booking()
        with self.assertRaises(ValidationError):
            booking.date = tuesday

    def test_03_capacity_limit(self):
        bookings = self.env["dock.booking"]
        for _index in range(3):
            bookings |= self._booking()
        self.assertEqual(len(bookings), 3)
        bookings[0].action_confirm()
        bookings[1].action_confirm()
        # The bookings are on another date: today's places are untouched.
        self.assertEqual(self.slot.available_count, self.slot.capacity)
        with self.assertRaises(UserError):
            bookings[2].action_confirm()
        self.assertEqual(bookings[2].state, "draft")
        with self.assertRaises(ValidationError):
            self._booking(state="confirmed")

    def test_04_workflow_and_state_guards(self):
        booking = self._booking()
        self.assertEqual(booking.state, "draft")
        with self.assertRaises(UserError):
            booking.action_done()
        with self.assertRaises(UserError):
            booking.action_reset()
        self.assertTrue(booking.action_confirm())
        self.assertEqual(booking.state, "confirmed")
        with self.assertRaises(UserError):
            booking.action_confirm()
        self.assertTrue(booking.action_done())
        self.assertEqual(booking.state, "done")
        with self.assertRaises(UserError):
            booking.action_cancel()
        with self.assertRaises(UserError):
            booking.action_reset()
        other = self._booking(partner=self.other_partner)
        self.assertTrue(other.action_cancel())
        self.assertEqual(other.state, "cancelled")
        self.assertTrue(other.action_reset())
        self.assertEqual(other.state, "draft")
        with self.assertRaises(UserError):
            other.action_reset()
        self.assertTrue(other.action_confirm())
        self.assertTrue(other.action_cancel())
        self.assertEqual(other.state, "cancelled")

    def test_05_blackout_blocks_confirmation(self):
        whole_day = self.env["dock.blackout"].create({
            "name": "Annual stocktake",
            "date": self.next_monday,
            "reason": "Warehouse closed all day.",
        })
        self.assertFalse(whole_day.slot_id)
        booking = self._booking(day=self.next_monday)
        with self.assertRaises(UserError):
            booking.action_confirm()
        self.assertEqual(booking.state, "draft")
        with self.assertRaises(ValidationError):
            self._booking(day=self.next_monday, state="confirmed")
        with self.assertRaises(ValidationError):
            self.env["dock.blackout"].create({
                "name": "Duplicate stocktake",
                "date": self.next_monday,
            })
        self.env["dock.blackout"].create({
            "name": "Dock A maintenance",
            "date": self.third_monday,
            "slot_id": self.slot.id,
        })
        blocked = self._booking(day=self.third_monday)
        with self.assertRaises(UserError):
            blocked.action_confirm()
        self.assertEqual(blocked.state, "draft")
        free = self._booking(slot=self.roomy_slot, day=self.third_monday)
        self.assertTrue(free.action_confirm())
        self.assertEqual(free.state, "confirmed")

    def test_06_available_count(self):
        today = fields.Date.context_today(self.env.user)
        slot = self._slot(
            name="Today window", weekday=str(today.weekday()),
            start_hour=9.0, end_hour=11.0, capacity=4)
        self.assertEqual(slot.available_count, 4)
        self.assertEqual(slot.booking_count, 0)
        booking = self._booking(slot=slot, day=today)
        self.assertEqual(slot.available_count, 4)
        self.assertEqual(slot.booking_count, 1)
        booking.action_confirm()
        slot.invalidate_recordset()
        self.assertEqual(slot.available_count, 3)
        booking.action_done()
        slot.invalidate_recordset()
        self.assertEqual(slot.available_count, 4)
        self.assertEqual(slot.booking_count, 1)
        other = self._booking(
            slot=slot, day=today, partner=self.other_partner)
        slot.invalidate_recordset()
        self.assertEqual(slot.booking_count, 2)
        other.action_cancel()
        slot.invalidate_recordset()
        self.assertEqual(slot.booking_count, 1)
        self.assertEqual(slot.available_count, 4)

    def test_07_slot_constraints(self):
        with self.assertRaises(ValidationError):
            self._slot(name="Inverted hours", start_hour=12.0, end_hour=8.0)
        with self.assertRaises(ValidationError):
            self._slot(name="Empty capacity", capacity=0)
        with self.assertRaises(ValidationError):
            self._slot(name="Start after midnight", start_hour=25.0,
                       end_hour=26.0)
        with self.assertRaises(ValidationError):
            self._slot(name="End after midnight", start_hour=8.0,
                       end_hour=25.0)

    def test_08_activate_and_archive(self):
        slot = self._slot(
            name="Wednesday window", weekday="2",
            start_hour=10.0, end_hour=12.0, capacity=3)
        self.assertTrue(slot.active)
        self.assertTrue(slot.action_archive())
        self.assertFalse(slot.active)
        self.assertNotIn(slot, self.env["dock.slot"].search([]))
        self.assertTrue(slot.action_activate())
        self.assertTrue(slot.active)
        self.assertIn(slot, self.env["dock.slot"].search([]))
