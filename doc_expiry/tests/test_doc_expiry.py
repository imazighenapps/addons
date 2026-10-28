# -*- coding: utf-8 -*-
from datetime import timedelta

from psycopg2 import IntegrityError

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDocExpiry(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.context_today(cls.env["expiry.document"])
        cls.category = cls.env["expiry.category"].create({
            "name": "DocExpiry Test Insurance",
            "code": "CAT-TEST-INS",
            "default_validity_days": 365,
            "reminder_days": 30,
        })
        cls.partner = cls.env["res.partner"].create({
            "name": "DocExpiry Test Insurer",
        })

    def _document(self, **kwargs):
        values = {
            "name": "Liability insurance",
            "reference": "DOC-TEST-001",
            "category_id": self.category.id,
            "partner_id": self.partner.id,
            "issue_date": self.today,
        }
        values.update(kwargs)
        return self.env["expiry.document"].create(values)

    def test_01_category_validity_applied_on_create(self):
        document = self._document(reference="DOC-TEST-VAL")
        self.assertEqual(
            document.expiry_date,
            self.today + timedelta(days=365))
        self.assertEqual(document.reminder_days, 30)

    def test_02_state_follows_expiry_date(self):
        valid = self._document(
            reference="DOC-TEST-VALID",
            expiry_date=self.today + timedelta(days=90))
        expiring = self._document(
            reference="DOC-TEST-EXPIRING",
            expiry_date=self.today + timedelta(days=10))
        expired = self._document(
            reference="DOC-TEST-EXPIRED",
            issue_date=self.today - timedelta(days=400),
            expiry_date=self.today - timedelta(days=1))
        self.assertEqual(valid.state, "valid")
        self.assertEqual(expiring.state, "expiring")
        self.assertEqual(expired.state, "expired")

    def test_03_days_left_and_reminder_date(self):
        document = self._document(
            reference="DOC-TEST-DAYS",
            expiry_date=self.today + timedelta(days=45))
        self.assertEqual(document.days_left, 45)
        self.assertEqual(
            document.reminder_date,
            self.today + timedelta(days=15))
        document.expiry_date = self.today + timedelta(days=5)
        self.assertEqual(document.days_left, 5)
        self.assertEqual(document.state, "expiring")

    def test_04_renew_moves_dates_and_logs_history(self):
        document = self._document(
            reference="DOC-TEST-RENEW",
            expiry_date=self.today + timedelta(days=5))
        old_expiry = document.expiry_date
        document.action_renew()
        self.assertEqual(document.issue_date, self.today)
        self.assertEqual(
            document.expiry_date,
            self.today + timedelta(days=365))
        renewal = document.log_ids.filtered(
            lambda log: log.action == "renewed")
        self.assertEqual(len(renewal), 1)
        self.assertEqual(renewal.old_expiry, old_expiry)
        self.assertEqual(renewal.new_expiry, document.expiry_date)

    def test_05_archive_and_restore(self):
        document = self._document(reference="DOC-TEST-ARCH")
        document.action_archive()
        self.assertFalse(document.active)
        self.assertTrue(document.log_ids.filtered(
            lambda log: log.action == "archived"))
        document.action_activate()
        self.assertTrue(document.active)

    def test_06_expiry_before_issue_is_refused(self):
        with self.assertRaises(ValidationError):
            self._document(
                reference="DOC-TEST-BADDATE",
                issue_date=self.today,
                expiry_date=self.today - timedelta(days=10))

    def test_07_reference_is_unique_per_company(self):
        self._document(reference="DOC-TEST-DUP")
        with self.assertRaises(IntegrityError):
            self._document(reference="DOC-TEST-DUP")
            self.env.flush_all()

    def test_08_cron_logs_one_reminder_per_day(self):
        document = self._document(
            reference="DOC-TEST-CRON",
            expiry_date=self.today + timedelta(days=10))
        self.env["expiry.document"]._cron_check_expiry()
        reminders = document.log_ids.filtered(
            lambda log: log.action == "reminder")
        self.assertEqual(len(reminders), 1)
        self.env["expiry.document"]._cron_check_expiry()
        reminders = document.log_ids.filtered(
            lambda log: log.action == "reminder")
        self.assertEqual(len(reminders), 1)
