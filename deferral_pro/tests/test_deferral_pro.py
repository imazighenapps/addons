# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDeferralPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "DeferralPro Test Partner",
        })

    def setUp(self):
        super().setUp()
        self._code_counter = 0

    def _code(self):
        self._code_counter += 1
        return "DFR-TEST-%03d" % self._code_counter

    def _schedule(self, **kwargs):
        values = {
            "name": "DeferralPro Test Schedule",
            "code": self._code(),
            "schedule_type": "expense",
            "partner_id": self.partner.id,
            "invoice_ref": "BILL/2026/0001",
            "amount": 1200.0,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 6, 30),
        }
        values.update(kwargs)
        return self.env["deferral.schedule"].create(values)

    def test_01_start_generates_monthly_lines(self):
        schedule = self._schedule()
        self.assertEqual(schedule.state, "draft")
        self.assertEqual(schedule.period_count, 6)
        self.assertTrue(schedule.action_start())
        self.assertEqual(schedule.state, "running")
        self.assertEqual(len(schedule.line_ids), 6)
        self.assertAlmostEqual(
            sum(schedule.line_ids.mapped("amount")), 1200.0, places=2)
        self.assertEqual(
            min(schedule.line_ids.mapped("date")), date(2026, 1, 1))
        self.assertEqual(
            max(schedule.line_ids.mapped("date")), date(2026, 6, 1))
        with self.assertRaises(UserError):
            schedule.action_start()

    def test_02_monthly_amount_and_remaining(self):
        schedule = self._schedule(amount=1500.0)
        self.assertEqual(schedule.period_count, 6)
        self.assertAlmostEqual(schedule.monthly_amount, 250.0, places=2)
        self.assertAlmostEqual(schedule.remaining_amount, 1500.0, places=2)
        schedule.action_start()
        self.assertAlmostEqual(schedule.posted_amount, 0.0, places=2)
        schedule.line_ids[0].action_post()
        self.assertAlmostEqual(schedule.posted_amount, 250.0, places=2)
        self.assertAlmostEqual(schedule.remaining_amount, 1250.0, places=2)
        self.assertEqual(schedule.state, "running")

    def test_03_post_next_posts_one_line(self):
        schedule = self._schedule()
        schedule.action_start()
        self.assertTrue(schedule.action_post_next())
        posted = schedule.line_ids.filtered(
            lambda line: line.state == "posted")
        self.assertEqual(len(posted), 1)
        self.assertAlmostEqual(schedule.posted_amount, 200.0, places=2)
        self.assertFalse(posted.move_id)
        self.assertEqual(schedule.state, "running")
        self.assertAlmostEqual(schedule.remaining_amount, 1000.0, places=2)

    def test_04_post_all_with_journal_entries(self):
        journal = self.env["account.journal"].search([
            ("type", "=", "general"),
            ("company_id", "=", self.env.company.id),
        ], limit=1)
        domain = []
        account_model = self.env["account.account"]
        if "account_type" in account_model._fields:
            domain.append(("account_type", "not in", ["view", "off_balance"]))
        if "company_ids" in account_model._fields:
            domain.append(("company_ids", "in", self.env.company.id))
        elif "company_id" in account_model._fields:
            domain.append(("company_id", "=", self.env.company.id))
        accounts = account_model.search(domain, limit=2)
        if not journal or len(accounts) < 2:
            self.skipTest(
                "No general journal or chart of accounts in this database.")
        schedule = self._schedule(
            amount=300.0,
            date_start=date(2026, 1, 1),
            date_end=date(2026, 3, 31),
            journal_id=journal.id,
            account_id=accounts[0].id,
            offset_account_id=accounts[1].id,
        )
        schedule.action_start()
        self.assertEqual(len(schedule.line_ids), 3)
        self.assertTrue(schedule.action_post_all())
        self.assertFalse(schedule.line_ids.filtered(
            lambda line: line.state == "draft"))
        self.assertEqual(len(schedule.line_ids.mapped("move_id")), 3)
        self.assertEqual(set(schedule.line_ids.mapped("move_id.state")),
                         {"posted"})
        self.assertAlmostEqual(schedule.posted_amount, 300.0, places=2)
        self.assertAlmostEqual(schedule.remaining_amount, 0.0, places=2)
        self.assertEqual(schedule.state, "done")

    def test_05_cannot_post_twice(self):
        schedule = self._schedule(
            amount=400.0, date_end=date(2026, 4, 30))
        schedule.action_start()
        schedule.action_post_all()
        self.assertEqual(schedule.state, "done")
        self.assertAlmostEqual(schedule.posted_amount, 400.0, places=2)
        with self.assertRaises(UserError):
            schedule.action_post_all()
        with self.assertRaises(UserError):
            schedule.action_post_next()
        with self.assertRaises(UserError):
            schedule.line_ids[0].action_post()

    def test_06_cancelled_schedule_cannot_post(self):
        schedule = self._schedule()
        schedule.action_start()
        self.assertTrue(schedule.action_cancel())
        self.assertEqual(schedule.state, "cancelled")
        with self.assertRaises(UserError):
            schedule.action_post_next()
        with self.assertRaises(UserError):
            schedule.line_ids[0].action_post()
        self.assertAlmostEqual(schedule.posted_amount, 0.0, places=2)
        self.assertTrue(schedule.action_reset())
        self.assertEqual(schedule.state, "draft")
        self.assertFalse(schedule.line_ids)
        with self.assertRaises(UserError):
            schedule.action_reset()

    def test_07_invalid_dates_and_amounts(self):
        with self.assertRaises(ValidationError):
            self._schedule(
                date_start=date(2026, 6, 30), date_end=date(2026, 1, 1))
        with self.assertRaises(ValidationError):
            self._schedule(amount=0.0)
        with self.assertRaises(ValidationError):
            self._schedule(amount=-250.0)
        schedule = self._schedule()
        self.assertAlmostEqual(schedule.amount, 1200.0, places=2)
        with self.assertRaises(ValidationError):
            schedule.write({"date_end": date(2025, 12, 31)})
        schedule.write({"note": "Twelve-month contract signed."})
        self.assertEqual(schedule.note, "Twelve-month contract signed.")

    def test_08_code_from_sequence_and_unique(self):
        schedule = self.env["deferral.schedule"].create({
            "amount": 600.0,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 3, 31),
        })
        self.assertTrue(schedule.code.startswith("DFR/"))
        self.assertEqual(schedule.name, schedule.code)
        self.assertEqual(schedule.period_count, 3)
        self.assertAlmostEqual(schedule.monthly_amount, 200.0, places=2)
        self._schedule(code="DFR-TEST-DUP")
        with self.assertRaises(ValidationError):
            self._schedule(code="DFR-TEST-DUP")
        self.assertEqual(
            self.env["deferral.schedule"].search_count([
                ("code", "=", "DFR-TEST-DUP")]), 1)
