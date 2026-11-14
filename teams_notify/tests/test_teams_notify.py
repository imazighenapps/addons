# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTeamsNotify(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel = cls.env["teams.channel"].create({
            "name": "Sales", "webhook_url": "https://example.com/hook",
        })

    def test_01_url_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["teams.channel"].create({"name": "Bad", "webhook_url": "ftp://x"})

    def test_02_activate(self):
        self.channel.action_activate(); self.assertEqual(self.channel.state, "active")

    def test_03_test_requires_active(self):
        with self.assertRaises(UserError): self.channel.action_test()

    def test_04_test_creates_notification(self):
        self.channel.action_activate()
        before = self.env["teams.notification"].search_count([("channel_id", "=", self.channel.id)])
        self.channel.action_test()
        after = self.env["teams.notification"].search_count([("channel_id", "=", self.channel.id)])
        self.assertEqual(after, before + 1)

    def test_05_send_notification(self):
        self.channel.action_activate()
        n = self.env["teams.notification"].create({
            "name": "N1", "channel_id": self.channel.id, "payload": "Hello",
        })
        n.action_send(); self.assertEqual(n.state, "sent")

    def test_06_send_requires_active_channel(self):
        n = self.env["teams.notification"].create({
            "name": "N2", "channel_id": self.channel.id, "payload": "Hi",
        })
        with self.assertRaises(UserError): n.action_send()

    def test_07_rule_create(self):
        r = self.env["teams.rule"].create({"name": "R", "channel_id": self.channel.id, "event_type": "sale"})
        self.assertEqual(r.company_id, self.channel.company_id)

    def test_08_inactive(self):
        self.channel.active = False
        self.assertFalse(self.channel.active)
