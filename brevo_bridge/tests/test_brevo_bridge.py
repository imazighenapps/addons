# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBrevoBridge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["brevo.connection"].create({
            "name": "Brevo Test", "api_key": "key", "sender_email": "info@test.com",
        })
        cls.partner = cls.env["res.partner"].create({"name": "Alice", "email": "alice@test.com"})
        cls.contact = cls.env["brevo.contact.sync"].create({
            "connection_id": cls.conn.id, "partner_id": cls.partner.id,
        })

    def test_01_activate_requires_key(self):
        c = self.env["brevo.connection"].create({"name": "No Key"})
        with self.assertRaises(UserError):
            c.action_activate()

    def test_02_sender_email_constraint(self):
        with self.assertRaises(ValidationError):
            self.conn.write({"sender_email": "bad"})

    def test_03_prepare_and_sync(self):
        self.conn.action_activate()
        self.contact.action_prepare()
        self.assertEqual(self.contact.state, "ready")
        self.contact.action_sync()
        self.assertEqual(self.contact.state, "synced")
        self.assertTrue(self.contact.brevo_contact_id)

    def test_04_sync_requires_ready(self):
        self.conn.action_activate()
        with self.assertRaises(UserError):
            self.contact.action_sync()

    def test_05_sync_requires_active_connection(self):
        self.contact.action_prepare()
        with self.assertRaises(UserError):
            self.contact.action_sync()

    def test_06_reset(self):
        self.conn.action_activate()
        self.contact.action_prepare()
        self.contact.action_sync()
        self.contact.action_reset()
        self.assertEqual(self.contact.state, "draft")

    def test_07_unique_partner_per_connection(self):
        with self.assertRaises(Exception):
            self.env["brevo.contact.sync"].create({
                "connection_id": self.conn.id, "partner_id": self.partner.id,
            })

    def test_08_email_required(self):
        p = self.env["res.partner"].create({"name": "NoMail"})
        with self.assertRaises(ValidationError):
            self.env["brevo.contact.sync"].create({
                "connection_id": self.conn.id, "partner_id": p.id,
            })
