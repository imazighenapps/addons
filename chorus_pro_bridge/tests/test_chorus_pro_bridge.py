# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestChorusProBridge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["chorus.pro.connection"].create({
            "name": "Chorus Test", "login": "tech@login",
        })
        cls.partner = cls.env["res.partner"].create({"name": "Public Entity"})
        cls.sub = cls.env["chorus.pro.submission"].create({
            "name": "CHR-TEST-001",
            "connection_id": cls.conn.id,
            "partner_id": cls.partner.id,
            "engagement_code": "EJ123",
            "amount_total": 500.0,
        })

    def test_01_activate_requires_login(self):
        c = self.env["chorus.pro.connection"].create({"name": "No Login"})
        with self.assertRaises(UserError):
            c.action_activate()
        c.login = "u"
        self.assertTrue(c.action_activate())
        self.assertEqual(c.state, "active")

    def test_02_prepare_requires_engagement(self):
        s = self.env["chorus.pro.submission"].create({
            "name": "CHR-TEST-002", "connection_id": self.conn.id,
            "amount_total": 10.0,
        })
        with self.assertRaises(UserError):
            s.action_prepare()

    def test_03_prepare_and_submit(self):
        self.conn.action_activate()
        self.sub.action_prepare()
        self.assertEqual(self.sub.state, "ready")
        self.sub.action_submit()
        self.assertEqual(self.sub.state, "submitted")
        self.assertTrue(self.sub.chorus_number)

    def test_04_submit_requires_active_connection(self):
        self.sub.action_prepare()
        with self.assertRaises(UserError):
            self.sub.action_submit()

    def test_05_accept_then_paid(self):
        self.conn.action_activate()
        self.sub.action_prepare()
        self.sub.action_submit()
        self.sub.action_mark_accepted()
        self.assertEqual(self.sub.state, "accepted")
        self.sub.action_mark_paid()
        self.assertEqual(self.sub.state, "paid")

    def test_06_reject_then_reprepare(self):
        self.conn.action_activate()
        self.sub.action_prepare()
        self.sub.action_submit()
        self.sub.action_mark_rejected()
        self.assertEqual(self.sub.state, "rejected")
        self.sub.action_prepare()
        self.assertEqual(self.sub.state, "ready")

    def test_07_status_logs_created(self):
        self.conn.action_activate()
        self.sub.action_prepare()
        self.sub.action_submit()
        self.assertTrue(self.sub.status_log_ids)

    def test_08_negative_amount(self):
        with self.assertRaises(ValidationError):
            self.env["chorus.pro.submission"].create({
                "name": "CHR-NEG", "connection_id": self.conn.id,
                "amount_total": -1.0,
            })
