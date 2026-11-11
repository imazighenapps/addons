# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestConsentBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ConsentBook Other Company",
        })
        cls.subject = cls.env["consent.subject"].create({
            "name": "ConsentBook Test Contact",
            "email": "consentbook.test@example.com",
        })
        cls.subject_b = cls.env["consent.subject"].create({
            "name": "ConsentBook Test Contact B",
            "email": "consentbook.test.b@example.com",
        })

    def _record(self, subject=None, **values):
        defaults = {
            "name": "ConsentBook Test Newsletter",
            "subject_id": (subject or self.subject).id,
            "channel": "email",
            "source": "ConsentBook Test Web Form",
            "proof_ref": "CB-PROOF-001",
            "granted_on": date(2026, 11, 10),
        }
        defaults.update(values)
        return self.env["consent.record"].create(defaults)

    def test_01_record_defaults(self):
        record = self._record()
        self.assertEqual(record.state, "active")
        self.assertEqual(record.company_id, self.env.company)
        self.assertEqual(record.channel, "email")
        self.assertFalse(record.withdrawn_on)

    def test_02_withdraw_requires_reason(self):
        record = self._record()
        with self.assertRaises(UserError):
            record.action_withdraw()
        record.withdrawal_reason = "ConsentBook Test unsubscribe request"
        self.assertTrue(record.action_withdraw())
        self.assertEqual(record.state, "withdrawn")
        self.assertTrue(record.withdrawn_on)

    def test_03_double_withdraw_is_refused(self):
        record = self._record()
        record.withdrawal_reason = "ConsentBook Test reason"
        record.action_withdraw()
        with self.assertRaises(UserError):
            record.action_withdraw()

    def test_04_expire_and_reactivate(self):
        record = self._record(name="ConsentBook Test Offers")
        self.assertTrue(record.action_expire())
        self.assertEqual(record.state, "expired")
        with self.assertRaises(UserError):
            record.action_expire()
        self.assertTrue(record.action_reactivate())
        self.assertEqual(record.state, "active")
        with self.assertRaises(UserError):
            record.action_reactivate()

    def test_05_dates_are_validated(self):
        with self.assertRaises(ValidationError):
            self._record(granted_on=date(2026, 11, 10),
                         expires_on=date(2026, 11, 1))
        with self.assertRaises(ValidationError):
            self._record(granted_on=date(2026, 11, 10),
                         withdrawn_on=date(2026, 11, 5))

    def test_06_subject_counters(self):
        active = self._record(name="ConsentBook Test Active")
        withdrawn = self._record(name="ConsentBook Test Withdrawn")
        withdrawn.withdrawal_reason = "ConsentBook Test stop"
        withdrawn.action_withdraw()
        self.subject.invalidate_recordset()
        self.assertEqual(self.subject.consent_count, 2)
        self.assertEqual(self.subject.active_consent_count, 1)
        self.assertEqual(active.state, "active")

    def test_07_company_isolation(self):
        foreign_subject = self.env["consent.subject"].with_company(
            self.other_company).sudo().create({
            "name": "ConsentBook Test Foreign Contact",
            "company_id": self.other_company.id,
        })
        foreign = self.env["consent.record"].with_company(
            self.other_company).sudo().create({
            "name": "ConsentBook Test Foreign Consent",
            "subject_id": foreign_subject.id,
            "source": "ConsentBook Test Foreign Source",
            "granted_on": date(2026, 12, 1),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._record(name="ConsentBook Test Local")
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)

    def test_08_filters_by_state(self):
        active = self._record(name="ConsentBook Test Active Filter")
        withdrawn = self._record(name="ConsentBook Test Withdrawn Filter")
        withdrawn.withdrawal_reason = "ConsentBook Test filter reason"
        withdrawn.action_withdraw()
        found = self.env["consent.record"].search([
            ("state", "=", "withdrawn"),
            ("subject_id", "=", self.subject.id),
        ])
        self.assertIn(withdrawn, found)
        self.assertNotIn(active, found)
