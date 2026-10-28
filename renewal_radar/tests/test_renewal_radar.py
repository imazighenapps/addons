# -*- coding: utf-8 -*-
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRenewalRadar(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "RenewalRadar Test Customer", "is_company": True})

    def _today(self):
        return fields.Date.context_today(self.env.user)

    def _contract(self, **kwargs):
        today = self._today()
        values = {
            "partner_id": self.partner.id,
            "contract_type": "subscription",
            "start_date": today - timedelta(days=300),
            "end_date": today + timedelta(days=20),
            "notice_days": 30,
            "term_months": 12,
            "amount": 1200.0,
        }
        values.update(kwargs)
        return self.env["renewal.contract"].create(values)

    def test_01_computed_dates(self):
        contract = self._contract()
        self.assertTrue(contract.name.startswith("CTR/"))
        self.assertEqual(
            contract.renewal_date,
            contract.end_date - timedelta(days=30))
        self.assertEqual(contract.days_left, 20)
        self.assertFalse(contract.is_expiring)
        contract.action_activate()
        self.assertTrue(contract.is_expiring)

    def test_02_cron_flags_due_contracts(self):
        today = self._today()
        contract = self._contract(end_date=today + timedelta(days=5))
        contract.action_activate()
        self.assertTrue(contract.renewal_date <= today)
        count = self.env["renewal.contract"]._cron_mark_to_renew()
        self.assertGreaterEqual(count, 1)
        self.assertEqual(contract.state, "to_renew")
        reminder = [("contract_id", "=", contract.id),
                    ("action", "=", "reminder")]
        self.assertEqual(self.env["renewal.log"].search_count(reminder), 1)
        self.env["renewal.contract"]._cron_mark_to_renew()
        self.assertEqual(contract.state, "to_renew")
        self.assertEqual(self.env["renewal.log"].search_count(reminder), 1)

    def test_03_renew_extends_term(self):
        today = self._today()
        contract = self._contract()
        contract.action_activate()
        old_end = contract.end_date
        contract.action_renew()
        self.assertEqual(
            contract.end_date, old_end + relativedelta(months=12))
        self.assertEqual(contract.renewal_count, 1)
        self.assertEqual(contract.last_renewal_date, today)
        self.assertEqual(contract.state, "active")
        log = self.env["renewal.log"].search([
            ("contract_id", "=", contract.id),
            ("action", "=", "renewed"),
        ], limit=1)
        self.assertTrue(log)
        self.assertEqual(log.user_id, self.env.user)

    def test_04_churn_requires_reason(self):
        contract = self._contract()
        contract.action_activate()
        with self.assertRaises(UserError):
            contract.action_churn()
        contract.churn_reason = "Customer moved to a competitor."
        contract.action_churn()
        self.assertEqual(contract.state, "churned")
        self.assertTrue(self.env["renewal.log"].search([
            ("contract_id", "=", contract.id),
            ("action", "=", "churned"),
        ], limit=1))

    def test_05_cannot_renew_churned(self):
        contract = self._contract()
        contract.action_activate()
        contract.churn_reason = "Budget cut."
        contract.action_churn()
        with self.assertRaises(UserError):
            contract.action_renew()

    def test_06_end_date_constraint(self):
        with self.assertRaises(ValidationError):
            self._contract(
                start_date=date(2026, 5, 10),
                end_date=date(2026, 5, 1))

    def test_07_workflow(self):
        contract = self._contract()
        self.assertEqual(contract.state, "draft")
        contract.action_activate()
        self.assertEqual(contract.state, "active")
        with self.assertRaises(UserError):
            contract.action_activate()
        contract.action_mark_to_renew()
        self.assertEqual(contract.state, "to_renew")
        contract.action_expire()
        self.assertEqual(contract.state, "expired")
        contract.action_reset()
        self.assertEqual(contract.state, "draft")

    def test_08_term_and_notice_constraints(self):
        with self.assertRaises(ValidationError):
            self._contract(term_months=0)
        with self.assertRaises(ValidationError):
            self._contract(notice_days=-1)
