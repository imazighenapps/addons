# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMailDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "MailDesk Other Company"})

    def _item(self, **values):
        defaults = {
            "name": "MAIL 2026-11-09-A",
            "direction": "inbound",
            "partner_name": "MailDesk Test Sender",
            "tracking_number": "TRK-001",
            "logged_on": date(2026, 11, 9),
        }
        defaults.update(values)
        return self.env["mail.item"].create(defaults)

    def test_01_item_defaults(self):
        record = self._item(name="MAIL 2026-11-09-DEF")
        self.assertEqual(record.state, "waiting")
        self.assertEqual(record.direction, "inbound")
        self.assertEqual(record.company_id, self.env.company)
        self.assertFalse(record.collected_on)

    def test_02_collect_stamps_date_and_user(self):
        record = self._item(name="MAIL 2026-11-10-A")
        self.assertTrue(record.action_collect())
        self.assertEqual(record.state, "collected")
        self.assertTrue(record.collected_on)
        self.assertTrue(record.collected_by)

    def test_03_double_collect_is_refused(self):
        record = self._item(name="MAIL 2026-11-10-B")
        record.action_collect()
        with self.assertRaises(UserError):
            record.action_collect()

    def test_04_collect_before_logged_is_refused(self):
        with self.assertRaises(ValidationError):
            self._item(
                name="MAIL 2026-11-10-C",
                logged_on=date(2026, 11, 9),
                collected_on=date(2026, 11, 2))

    def test_05_outbound_direction(self):
        record = self._item(name="MAIL 2026-11-11-A",
                            direction="outbound",
                            partner_name="MailDesk Test Recipient")
        self.assertEqual(record.direction, "outbound")
        self.assertEqual(record.partner_name, "MailDesk Test Recipient")

    def test_06_tracking_number_stored(self):
        record = self._item(name="MAIL 2026-11-11-B",
                            tracking_number="TRK-XYZ-2026")
        self.assertEqual(record.tracking_number, "TRK-XYZ-2026")

    def test_07_waiting_search_finds_uncollected_only(self):
        waiting = self._item(name="MAIL 2026-11-12-A")
        done = self._item(name="MAIL 2026-11-12-B")
        done.action_collect()
        found = self.env["mail.item"].search([
            ("state", "=", "waiting"),
            ("name", "in", [waiting.name, done.name])])
        self.assertIn(waiting, found)
        self.assertNotIn(done, found)

    def test_08_company_isolation(self):
        foreign = self.env["mail.item"].with_company(
            self.other_company).sudo().create({
            "name": "MAIL 2026-11-12-FOREIGN",
            "direction": "inbound",
            "partner_name": "Foreign Sender",
            "tracking_number": "TRK-F-001",
            "logged_on": date(2026, 11, 12),
            "company_id": self.other_company.id,
        })
        local = self._item(name="MAIL 2026-11-12-C")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
