# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestQuotePing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "QuotePing Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "QuotePing Test Customer"})

    def _watch(self, **values):
        defaults = {
            "quote_ref": "QuotePing Test Quote Q-101",
            "partner_id": self.partner.id,
            "amount": 9600.0,
            "quote_on": date(2026, 6, 1),
            "remind_every": 5,
            "max_reminders": 3,
        }
        defaults.update(values)
        return self.env["quote.watch"].create(defaults)

    def _nudge(self, watch, **values):
        defaults = {
            "watch_id": watch.id,
            "nudge_on": date(2026, 8, 17),
        }
        defaults.update(values)
        return self.env["quote.nudge"].create(defaults)

    def test_01_watch_defaults(self):
        watch = self._watch()
        self.assertTrue(watch.name.startswith("QPW/"))
        self.assertEqual(watch.state, "watching")
        self.assertEqual(watch.nudge_count, 0)
        self.assertEqual(watch.remind_every, 5)
        self.assertEqual(watch.max_reminders, 3)
        self.assertEqual(watch.company_id, self.env.company)
        self.assertEqual(watch.amount, 9600.0)

    def test_02_due_flag_comes_from_the_plan(self):
        watch = self._watch()
        self.assertTrue(watch.is_due)
        planned = self._watch(quote_on=fields.Date.context_today(
            self.env["quote.watch"]))
        self.assertFalse(planned.is_due)
        spaced = self._watch(quote_ref="QuotePing Test Quote Q-202",
                             remind_every=600)
        self.assertFalse(spaced.is_due)

    def test_03_remind_logs_a_nudge(self):
        watch = self._watch()
        self.assertTrue(watch.action_nudge())
        self.assertEqual(watch.nudge_count, 1)
        self.assertEqual(watch.nudge_ids[0].channel, "email")
        self.assertEqual(watch.nudge_ids[0].user_id, self.env.user)
        self.assertTrue(watch.message_ids)

    def test_04_maximum_reminders_is_enforced(self):
        watch = self._watch(max_reminders=2)
        self.assertTrue(watch.action_nudge())
        self.assertTrue(watch.action_nudge())
        self.assertEqual(watch.nudge_count, 2)
        with self.assertRaises(UserError):
            watch.action_nudge()
        with self.assertRaises(UserError):
            self._nudge(watch)
        self.assertEqual(watch.nudge_count, 2)

    def test_05_remind_only_watching_quotes(self):
        watch = self._watch()
        watch.action_lost()
        with self.assertRaises(UserError):
            watch.action_nudge()
        with self.assertRaises(UserError):
            self._nudge(watch)
        self.assertEqual(watch.state, "lost")
        self.assertEqual(watch.nudge_count, 0)

    def test_06_won_and_lost_close_the_tracker(self):
        won = self._watch(quote_ref="QuotePing Test Quote Q-303")
        self.assertTrue(won.action_won())
        self.assertEqual(won.state, "won")
        self.assertFalse(won.is_due)
        lost = self._watch()
        lost.action_lost()
        self.assertEqual(lost.state, "lost")
        with self.assertRaises(UserError):
            won.action_won()
        with self.assertRaises(UserError):
            won.action_lost()

    def test_07_plan_must_be_sane(self):
        with self.assertRaises(ValidationError):
            self._watch(remind_every=0)
        with self.assertRaises(ValidationError):
            self._watch(max_reminders=0)
        with self.assertRaises(ValidationError):
            self._watch(amount=-10.0)

    def test_08_last_nudge_and_more_nudges(self):
        watch = self._watch()
        first = self._nudge(watch, nudge_on=date(2026, 8, 17),
                            channel="phone")
        second = self._nudge(watch, nudge_on=date(2026, 9, 4),
                             channel="meeting",
                             feedback="QuotePing Test Meeting Booked")
        watch.invalidate_recordset()
        self.assertEqual(watch.nudge_count, 2)
        self.assertEqual(watch.last_nudge_on, date(2026, 9, 4))
        self.assertEqual(first.feedback, False)
        self.assertTrue(second)
        self.assertIn(watch, self.env["quote.watch"].search(
            [("nudge_count", ">", 0)]))

    def test_09_company_isolation(self):
        foreign = self.env["quote.watch"].with_company(
            self.other_company).sudo().create({
            "quote_ref": "QuotePing Test Quote Q-FOR",
            "quote_on": date(2026, 6, 1),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._watch()
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
        foreign_nudge = self.env["quote.nudge"].with_company(
            self.other_company).sudo().create({
            "watch_id": foreign.id,
            "nudge_on": date(2026, 8, 17),
        })
        self.assertEqual(foreign_nudge.company_id, self.other_company)
        local_nudge = self._watch()
        local_nudge.action_nudge()
        self.assertEqual(local_nudge.nudge_ids[0].company_id,
                         self.env.company)

    def test_10_search_filters(self):
        due = self._watch(quote_ref="QuotePing Test Quote Q-404")
        closed = self._watch(quote_ref="QuotePing Test Quote Q-505")
        closed.action_won()
        watches = self.env["quote.watch"]
        self.assertIn(due, watches.search([("is_due", "=", True)]))
        self.assertIn(due, watches.search(
            [("state", "=", "watching")]))
        self.assertIn(closed, watches.search(
            [("state", "in", ["won", "lost"])]))
        self.assertNotIn(closed, watches.search(
            [("is_due", "=", True)]))
        nudges = self.env["quote.nudge"].search([])
        self.assertTrue(all(nudge.company_id for nudge in nudges))
