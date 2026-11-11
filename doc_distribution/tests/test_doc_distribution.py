# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDocDistribution(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "DocFlow Other Company"})
        cls.recipient = cls.env["res.partner"].create({
            "name": "DocFlow Test Recipient"})
        cls.recipient_two = cls.env["res.partner"].create({
            "name": "DocFlow Test Recipient Two"})
        cls.document = cls.env["doc.control"].create({
            "name": "DocFlow Test Procedure",
            "code": "SOP-001",
            "revision": "B",
            "effective_on": date(2026, 11, 1),
        })

    def _distribution(self, document=None, recipient=None, **values):
        defaults = {
            "document_id": (document or self.document).id,
            "recipient_id": (recipient or self.recipient).id,
            "sent_on": date(2026, 11, 9),
        }
        defaults.update(values)
        return self.env["doc.distribution"].create(defaults)

    def test_01_distribution_defaults(self):
        line = self._distribution()
        self.assertEqual(line.state, "pending")
        self.assertEqual(line.company_id, self.env.company)
        self.assertTrue(line.name.startswith("Distribution "))
        self.assertFalse(line.acknowledged_on)

    def test_02_acknowledge_stamps_the_date(self):
        line = self._distribution()
        self.assertTrue(line.action_acknowledge())
        self.assertEqual(line.state, "acknowledged")
        self.assertTrue(line.acknowledged_on)

    def test_03_double_acknowledge_is_refused(self):
        line = self._distribution()
        line.action_acknowledge()
        with self.assertRaises(ValidationError):
            line.action_acknowledge()

    def test_04_ack_before_sent_is_refused(self):
        with self.assertRaises(ValidationError):
            self._distribution(sent_on=date(2026, 11, 9),
                               acknowledged_on=date(2026, 11, 2))

    def test_05_duplicate_recipient_is_refused(self):
        self._distribution()
        with self.assertRaises(ValidationError):
            self._distribution(sent_on=date(2026, 11, 10))

    def test_06_different_recipients_are_allowed(self):
        first = self._distribution()
        second = self._distribution(recipient=self.recipient_two)
        self.assertNotEqual(first.recipient_id, second.recipient_id)

    def test_07_document_counters(self):
        pending = self._distribution()
        acked = self._distribution(recipient=self.recipient_two)
        acked.action_acknowledge()
        self.document.invalidate_recordset()
        self.assertEqual(self.document.distribution_count, 2)
        self.assertEqual(self.document.pending_count, 1)
        self.assertEqual(self.document.acknowledged_count, 1)
        self.assertTrue(pending)

    def test_08_company_isolation(self):
        foreign_recipient = self.env["res.partner"].sudo().create({
            "name": "DocFlow Test Foreign Recipient"})
        foreign = self.env["doc.distribution"].with_company(
            self.other_company).sudo().create({
            "document_id": self.document.id,
            "recipient_id": foreign_recipient.id,
            "sent_on": date(2026, 11, 9),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._distribution()
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
