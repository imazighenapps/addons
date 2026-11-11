# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestChurnWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ChurnWatch Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "ChurnWatch Test Customer"})
        cls.signal = cls.env["churn.signal"].create({
            "name": "ChurnWatch Signal A",
            "partner_id": cls.partner.id,
            "last_order_date": date(2026, 1, 10),
            "silence_threshold": 30,
        })

    def _action(self, **values):
        defaults = {
            "name": "ChurnWatch Save Action",
            "signal_id": self.signal.id,
            "planned_date": date(2026, 11, 5),
            "outcome": "pending",
        }
        defaults.update(values)
        return self.env["churn.action"].create(defaults)

    def test_01_signal_defaults(self):
        self.assertEqual(self.signal.state, "watching")
        self.assertEqual(self.signal.company_id, self.env.company)
        self.assertTrue(self.signal.days_silent >= 0)
        self.assertEqual(self.signal.action_count, 0)

    def test_02_risk_flag_from_threshold(self):
        risky = self.env["churn.signal"].create({
            "name": "ChurnWatch Risky",
            "partner_id": self.partner.id,
            "last_order_date": fields.Date.today() - timedelta(days=45),
            "silence_threshold": 30,
        })
        fresh = self.env["churn.signal"].create({
            "name": "ChurnWatch Fresh",
            "partner_id": self.partner.id,
            "last_order_date": fields.Date.today(),
            "silence_threshold": 30,
        })
        self.assertTrue(risky.is_at_risk)
        self.assertFalse(fresh.is_at_risk)

    def test_03_action_count_updates(self):
        self._action()
        self._action(name="ChurnWatch Save Action 2",
                     planned_date=date(2026, 11, 6))
        self.signal.invalidate_recordset()
        self.assertEqual(self.signal.action_count, 2)

    def test_04_mark_saved_and_lost(self):
        self.assertTrue(self.signal.action_mark_saved())
        self.assertEqual(self.signal.state, "saved")
        other = self.env["churn.signal"].create({
            "name": "ChurnWatch Lost Signal",
            "partner_id": self.partner.id,
            "last_order_date": date(2026, 2, 1),
            "silence_threshold": 20,
        })
        self.assertTrue(other.action_mark_lost())
        self.assertEqual(other.state, "lost")

    def test_05_action_done_requires_outcome(self):
        action = self._action(outcome="pending")
        with self.assertRaises(ValidationError):
            action.action_done()
        action.write({"outcome": "contacted"})
        self.assertTrue(action.action_done())
        self.assertTrue(action.done_date)

    def test_06_threshold_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.env["churn.signal"].create({
                "name": "ChurnWatch Bad Threshold",
                "partner_id": self.partner.id,
                "last_order_date": date(2026, 1, 1),
                "silence_threshold": 0,
            })

    def test_07_future_date_and_action_dates_refused(self):
        future = date.today() + timedelta(days=10)
        with self.assertRaises(ValidationError):
            self.env["churn.signal"].create({
                "name": "ChurnWatch Future",
                "partner_id": self.partner.id,
                "last_order_date": future,
                "silence_threshold": 10,
            })
        action = self._action(outcome="contacted",
                              planned_date=date(2026, 11, 10),
                              done_date=date(2026, 11, 12))
        with self.assertRaises(ValidationError):
            action.write({"done_date": date(2026, 11, 1)})

    def test_08_company_isolation(self):
        foreign_partner = self.env["res.partner"].sudo().create({
            "name": "ChurnWatch Foreign Customer"})
        foreign = self.env["churn.signal"].with_company(
            self.other_company).sudo().create({
            "name": "ChurnWatch Foreign Signal",
            "partner_id": foreign_partner.id,
            "last_order_date": date(2026, 3, 1),
            "silence_threshold": 15,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(self.signal.company_id, self.env.company)

from odoo import fields  # noqa: E402
