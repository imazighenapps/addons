# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPennylaneBridge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Pennylane Customer"})
        cls.connection = cls.env["pennylane.connection"].create({
            "name": "Pennylane Test",
            "api_token": "test-token",
            "environment": "sandbox",
        })
        cls.export = cls.env["pennylane.export"].create({
            "name": "PNL-TEST-001",
            "connection_id": cls.connection.id,
            "document_type": "invoice",
            "partner_id": cls.partner.id,
            "amount_total": 120.0,
        })

    def test_01_activate_requires_token(self):
        conn = self.env["pennylane.connection"].create({"name": "No Token"})
        with self.assertRaises(UserError):
            conn.action_activate()
        conn.api_token = "abc"
        self.assertTrue(conn.action_activate())
        self.assertEqual(conn.state, "active")

    def test_02_prepare_export(self):
        self.assertEqual(self.export.state, "draft")
        self.assertTrue(self.export.action_prepare())
        self.assertEqual(self.export.state, "ready")
        self.assertTrue(self.export.payload)

    def test_03_send_requires_active_connection(self):
        self.export.action_prepare()
        with self.assertRaises(UserError):
            self.export.action_send()
        self.connection.action_activate()
        self.assertTrue(self.export.action_send())
        self.assertEqual(self.export.state, "sent")
        self.assertTrue(self.export.external_id)

    def test_04_reset_increments_retry(self):
        self.export.action_prepare()
        self.export.state = "error"
        self.assertEqual(self.export.retry_count, 0)
        self.assertTrue(self.export.action_reset())
        self.assertEqual(self.export.state, "draft")
        self.assertEqual(self.export.retry_count, 1)

    def test_05_sent_export_cannot_reset(self):
        self.connection.action_activate()
        self.export.action_prepare()
        self.export.action_send()
        with self.assertRaises(UserError):
            self.export.action_reset()

    def test_06_test_connection_logs(self):
        self.connection.action_activate()
        before = self.env["pennylane.sync.log"].search_count([
            ("connection_id", "=", self.connection.id), ("action", "=", "test")])
        self.connection.action_test_connection()
        after = self.env["pennylane.sync.log"].search_count([
            ("connection_id", "=", self.connection.id), ("action", "=", "test")])
        self.assertEqual(after, before + 1)

    def test_07_amount_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["pennylane.export"].create({
                "name": "PNL-NEG",
                "connection_id": self.connection.id,
                "amount_total": -5.0,
            })

    def test_08_base_url_constraint(self):
        with self.assertRaises(ValidationError):
            self.connection.write({"base_url": "ftp://invalid"})
