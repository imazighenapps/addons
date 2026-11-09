# -*- coding: utf-8 -*-
from datetime import date, datetime

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestMinuteBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "MinuteBook Test Attendee",
        })
        cls.minute = cls.env["meeting.minute"].create({
            "name": "MinuteBook Test Weekly Steering",
            "date_meeting": datetime(2026, 3, 4, 9, 0),
            "location": "Room A",
            "attendee_ids": [(6, 0, [cls.partner.id])],
            "agenda": "Budget, planning, risks.",
        })

    def _minute(self, name="MinuteBook Test Weekly", **kwargs):
        values = {
            "name": name,
            "date_meeting": datetime(2026, 3, 4, 9, 0),
            "attendee_ids": [(6, 0, [self.partner.id])],
        }
        values.update(kwargs)
        return self.env["meeting.minute"].create(values)

    def _action(self, name, minute=None, **kwargs):
        values = {
            "minute_id": (minute or self.minute).id,
            "name": name,
            "user_id": self.env.user.id,
        }
        values.update(kwargs)
        return self.env["meeting.action"].create(values)

    def test_01_close_without_decisions_is_refused(self):
        self.assertEqual(self.minute.state, "draft")
        self.assertTrue(self.minute.action_hold())
        self.assertEqual(self.minute.state, "held")
        with self.assertRaises(UserError):
            self.minute.action_close()
        self.assertEqual(self.minute.state, "held")
        with self.assertRaises(UserError):
            self.minute.action_hold()

    def test_02_close_with_decisions(self):
        self.minute.action_hold()
        self.minute.write({
            "decisions": "Hire one developer. Freeze the scope.",
        })
        self.assertTrue(self.minute.action_close())
        self.assertEqual(self.minute.state, "closed")
        with self.assertRaises(UserError):
            self.minute.action_cancel()
        self.assertTrue(self.minute.action_reset())
        self.assertEqual(self.minute.state, "draft")
        with self.assertRaises(UserError):
            self.minute.action_reset()

    def test_03_action_done_sets_done_date(self):
        action = self._action("Write the decision log",
                              due_date=date(2099, 1, 15))
        self.assertEqual(action.state, "todo")
        self.assertFalse(action.done_date)
        self.assertTrue(action.action_done())
        self.assertEqual(action.state, "done")
        self.assertEqual(action.done_date,
                         fields.Date.context_today(action))
        self.assertFalse(action.is_overdue)

    def test_04_overdue_with_a_past_due_date(self):
        action = self._action("Send the recap",
                              due_date=date(2000, 1, 1))
        self.assertEqual(action.state, "todo")
        self.assertTrue(action.is_overdue)
        action.write({"state": "cancelled"})
        self.assertFalse(action.is_overdue)
        action.write({"state": "todo"})
        self.assertTrue(action.is_overdue)

    def test_05_not_overdue_with_a_future_due_date(self):
        action = self._action("Book the next room",
                              due_date=date(2099, 12, 31))
        self.assertFalse(action.is_overdue)
        self.assertTrue(action.action_done())
        self.assertFalse(action.is_overdue)
        open_action = self._action("Prepare the agenda")
        self.assertFalse(open_action.due_date)
        self.assertFalse(open_action.is_overdue)

    def test_06_reopen_a_done_action(self):
        action = self._action("Publish the minutes",
                              due_date=date(2099, 2, 1))
        action.action_done()
        self.assertEqual(action.state, "done")
        self.assertTrue(action.done_date)
        self.assertTrue(action.action_reopen())
        self.assertEqual(action.state, "todo")
        self.assertFalse(action.done_date)
        with self.assertRaises(UserError):
            action.action_reopen()

    def test_07_open_action_count(self):
        minute = self._minute(name="MinuteBook Test Counts")
        self.assertEqual(minute.action_count, 0)
        self.assertEqual(minute.open_action_count, 0)
        first = self._action("Draft the plan", minute=minute)
        second = self._action("Validate the budget", minute=minute)
        third = self._action("Book the room", minute=minute)
        minute.invalidate_recordset()
        self.assertEqual(minute.action_count, 3)
        self.assertEqual(minute.open_action_count, 3)
        first.action_done()
        third.action_cancel()
        minute.invalidate_recordset()
        self.assertEqual(minute.action_count, 3)
        self.assertEqual(minute.open_action_count, 1)
        self.assertEqual(second.state, "todo")

    def test_08_company_isolation(self):
        other = self.env["res.company"].create({
            "name": "MinuteBook Other Company",
        })
        mine = self._minute(name="MinuteBook Test Mine")
        foreign = self.env["meeting.minute"].sudo().with_company(
            other).create({
                "name": "MinuteBook Test Foreign",
                "date_meeting": datetime(2026, 4, 1, 9, 0),
                "company_id": other.id,
                "chair_id": self.env.user.id,
            })
        self.assertEqual(mine.company_id, self.env.company)
        self.assertEqual(foreign.company_id, other)
        # The module group opens the model, the company rule closes the
        # other company: a member of the first company never sees it.
        member = new_test_user(
            self.env, login="minutebook_iso",
            groups="base.group_user,"
                   "meeting_minutes_pro.group_meetingminut_user",
            company_id=self.env.company.id,
            company_ids=[(6, 0, [self.env.company.id])])
        seen = self.env["meeting.minute"].with_user(member).with_context(
            allowed_company_ids=[self.env.company.id]).search(
                [("name", "like", "MinuteBook Test ")])
        self.assertIn(mine, seen)
        self.assertNotIn(foreign, seen)
        action = self.env["meeting.action"].sudo().with_company(
            other).create({
                "minute_id": foreign.id,
                "name": "MinuteBook Foreign Action",
                "user_id": self.env.user.id,
            })
        self.assertEqual(action.company_id, other)
        seen_actions = self.env["meeting.action"].with_user(member) \
            .with_context(
                allowed_company_ids=[self.env.company.id]).search([])
        self.assertNotIn(action, seen_actions)
