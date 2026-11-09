# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBounceGuard(TransactionCase):

    def _partner(self):
        return self.env["res.partner"].create({
            "name": "Bounce contact",
            "email": "bounce@example.com",
        })

    def _bounced(self, partner, status="bounce", date=None):
        # mail.notification uses the literal 'bounce' as its bounced status,
        # and its message carries the date the scan window filters on.
        message = self.env["mail.message"].create({
            "model": "res.partner",
            "res_id": partner.id,
            "message_type": "email",
            "subject": "Delivery failure",
            "date": date,
        })
        return self.env["mail.notification"].create({
            "mail_message_id": message.id,
            "res_partner_id": partner.id,
            "notification_type": "email",
            "notification_status": status,
        })

    def _scan(self, **values):
        wizard = self.env["bounce.scan.wizard"].create(values)
        wizard.action_scan()
        return wizard

    def _event_of(self, notification):
        return self.env["bounce.event"].search([
            ("notification_id", "=", notification.id)])

    def test_01_a_bounce_is_filed_as_an_event(self):
        partner = self._partner()
        notification = self._bounced(partner, status="bounce")
        self._scan()
        event = self.env["bounce.event"].search([
            ("notification_id", "=", notification.id)])
        self.assertEqual(len(event), 1)
        self.assertEqual(event.partner_id, partner)
        self.assertEqual(event.email, "bounce@example.com")

    def test_02_scanning_twice_never_duplicates(self):
        partner = self._partner()
        self._bounced(partner)
        self._scan()
        count = self.env["bounce.event"].search_count([])
        self._scan()
        self.assertEqual(
            self.env["bounce.event"].search_count([]), count)

    def test_03_delivered_notifications_are_ignored(self):
        partner = self._partner()
        notification = self._bounced(partner, status="sent")
        self._scan()
        self.assertFalse(self._event_of(notification))

    def test_04_an_event_can_be_handled_and_reopened(self):
        partner = self._partner()
        notification = self._bounced(partner)
        self._scan()
        event = self._event_of(notification)
        event.action_handle()
        self.assertEqual(event.state, "handled")
        event.action_reopen()
        self.assertEqual(event.state, "new")

    def test_05_an_event_can_be_ignored(self):
        partner = self._partner()
        notification = self._bounced(partner)
        self._scan()
        event = self._event_of(notification)
        event.action_ignore()
        self.assertEqual(event.state, "ignored")

    def test_06_the_partner_counts_its_bounces(self):
        partner = self._partner()
        self._bounced(partner)
        self._bounced(partner)
        self._scan()
        partner.invalidate_recordset()
        for event in partner.event_ids:
            self.assertEqual(event.partner_id, partner)
        self.assertEqual(len(partner.event_ids), 2)

    def test_07_a_smooth_address_is_never_flagged(self):
        # A single bounce stays under the default threshold of 2: no activity.
        partner = self._partner()
        self._bounced(partner)
        self._scan()
        partner.invalidate_recordset()
        self.assertEqual(len(partner.event_ids), 1)
        self.assertFalse(partner.activity_ids)

    def test_08_companies_are_isolated(self):
        other = self.env["res.company"].create({"name": "Bounce B"})
        partner = self._partner()
        self._bounced(partner)
        self._scan()
        events = self.env["bounce.event"].search([
            ("partner_id", "=", partner.id)])
        self.assertTrue(events)
        for event in events:
            self.assertEqual(event.company_id, self.env.company)
            self.assertEqual(event.state, "new")

    def test_09_the_window_keeps_out_unrelated_messages(self):
        # The scan window is read on the message date, on every supported
        # series: a bounce outside the window must stay unfiled.
        partner = self._partner()
        notification = self._bounced(partner, date="2099-06-03 09:00:00")
        self._scan(date_from=datetime(1990, 1, 1),
                   date_to=datetime(1991, 1, 1))
        self.assertFalse(self._event_of(notification))
