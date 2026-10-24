# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTimeApprove(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.user

    def _week(self, start=date(2026, 3, 2)):
        return self.env["timesheet.week"].create({
            "user_id": self.user.id,
            "date_start": start,
        })

    def _line(self, day, hours, week=None, name="Work"):
        vals = {
            "name": name,
            "user_id": self.user.id,
            "date": day,
            "unit_amount": hours,
            "company_id": self.env.company.id,
        }
        if week:
            vals["timesheet_week_id"] = week.id
        return self.env["account.analytic.line"].create(vals)

    def test_01_week_dates(self):
        week = self._week(date(2026, 3, 4))
        self.assertEqual(week.date_start, date(2026, 3, 2))
        self.assertEqual(week.date_end, date(2026, 3, 8))
        self.assertTrue(week.name.startswith("TW/"))

    def test_02_generate_and_total(self):
        self._line(date(2026, 3, 2), 8.0)
        self._line(date(2026, 3, 3), 7.5)
        week = self._week()
        week.action_generate()
        self.assertEqual(len(week.line_ids), 2)
        self.assertAlmostEqual(week.total_hours, 15.5, places=2)

    def test_03_approval_flow(self):
        self._line(date(2026, 3, 2), 8.0)
        week = self._week()
        week.action_generate()
        week.action_submit()
        self.assertEqual(week.state, "submitted")
        self.assertTrue(week.submitted_on)
        week.action_approve()
        self.assertEqual(week.state, "approved")
        self.assertTrue(week.approved_by)
        self.assertTrue(week.approved_on)

    def test_04_locked_after_approval(self):
        line = self._line(date(2026, 3, 2), 8.0)
        week = self._week()
        line.timesheet_week_id = week
        week.action_submit()
        week.action_approve()
        with self.assertRaises(UserError):
            line.unit_amount = 4.0
        with self.assertRaises(UserError):
            self._line(date(2026, 3, 3), 2.0, week=week)

    def test_05_reject_requires_comment(self):
        self._line(date(2026, 3, 2), 8.0)
        week = self._week()
        week.action_generate()
        week.action_submit()
        with self.assertRaises(UserError):
            week.action_reject()
        week.comment = "Missing project code"
        week.action_reject()
        self.assertEqual(week.state, "rejected")

    def test_06_submit_empty_week(self):
        week = self._week()
        with self.assertRaises(UserError):
            week.action_submit()

    def test_07_cron_reminder(self):
        week = self._week(date(2020, 1, 6))
        count = self.env["timesheet.week"]._cron_remind()
        self.assertGreaterEqual(count, 1)
        self.assertTrue(week.activity_ids)

    def test_08_duplicate_week(self):
        self._week()
        with self.assertRaises(Exception):
            self._week()

    def test_09_string_date_is_normalized(self):
        week = self.env["timesheet.week"].create({
            "user_id": self.env.user.id,
            "date_start": "2026-03-04",
        })
        self.assertEqual(str(week.date_start), "2026-03-02")
        self.assertEqual(str(week.date_end), "2026-03-08")
