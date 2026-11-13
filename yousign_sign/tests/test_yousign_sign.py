# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestYousignSign(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["yousign.connection"].create({"name": "YS", "api_key_ref": "key"})
        cls.partner = cls.env["res.partner"].create({"name": "SignerCo"})
        cls.req = cls.env["yousign.request"].create({
            "name": "YS-1", "connection_id": cls.conn.id, "partner_id": cls.partner.id, "document_name": "Quote",
        })
        cls.signer = cls.env["yousign.signer"].create({
            "request_id": cls.req.id, "name": "Bob", "email": "bob@test.com",
        })

    def test_01_activate_requires_key(self):
        c = self.env["yousign.connection"].create({"name": "No"})
        with self.assertRaises(UserError): c.action_activate()

    def test_02_send_requires_active_and_signer(self):
        with self.assertRaises(UserError): self.req.action_send()
        self.conn.action_activate()
        r = self.env["yousign.request"].create({
            "name": "YS-2", "connection_id": self.conn.id, "document_name": "Doc",
        })
        with self.assertRaises(UserError): r.action_send()

    def test_03_send_and_sign(self):
        self.conn.action_activate()
        self.req.action_send()
        self.assertEqual(self.req.state, "sent")
        self.req.action_mark_signed()
        self.assertEqual(self.req.state, "signed")
        self.assertTrue(self.req.proof_ref)

    def test_04_decline(self):
        self.conn.action_activate(); self.req.action_send(); self.req.action_mark_declined()
        self.assertEqual(self.req.state, "declined")

    def test_05_expire(self):
        self.conn.action_activate(); self.req.action_send(); self.req.action_mark_expired()
        self.assertEqual(self.req.state, "expired")

    def test_06_signed_cannot_cancel(self):
        self.conn.action_activate(); self.req.action_send(); self.req.action_mark_signed()
        with self.assertRaises(UserError): self.req.action_cancel()

    def test_07_signer_email_invalid(self):
        with self.assertRaises(ValidationError):
            self.env["yousign.signer"].create({"request_id": self.req.id, "name": "X", "email": "bad"})

    def test_08_events(self):
        self.conn.action_activate(); self.req.action_send()
        self.assertTrue(self.req.event_ids)
