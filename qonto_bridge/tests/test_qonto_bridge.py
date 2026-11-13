# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestQontoBridge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["qonto.connection"].create({
            "name": "Qonto", "organization_slug": "acme", "token_ref": "tok",
        })
        cls.tx = cls.env["qonto.transaction"].create({
            "name": "QTO-001", "connection_id": cls.conn.id,
            "label": "Coffee", "amount": 12.5, "direction": "out",
        })

    def test_01_activate_requires_token(self):
        c = self.env["qonto.connection"].create({"name": "NoTok", "organization_slug": "x"})
        with self.assertRaises(UserError):
            c.action_activate()

    def test_02_sync_requires_active(self):
        with self.assertRaises(UserError):
            self.conn.action_sync()
        self.conn.action_activate()
        self.conn.action_sync()
        self.assertTrue(self.conn.last_sync_at)

    def test_03_match_ignore_reset(self):
        self.tx.action_match()
        self.assertEqual(self.tx.state, "matched")
        with self.assertRaises(UserError):
            self.tx.action_ignore()
        self.tx.action_reset()
        self.assertEqual(self.tx.state, "new")
        self.tx.action_ignore()
        self.assertEqual(self.tx.state, "ignored")

    def test_04_ignored_cannot_match(self):
        self.tx.action_ignore()
        with self.assertRaises(UserError):
            self.tx.action_match()

    def test_05_amount_not_zero(self):
        with self.assertRaises(ValidationError):
            self.env["qonto.transaction"].create({
                "name": "QTO-Z", "connection_id": self.conn.id,
                "label": "Zero", "amount": 0.0,
            })

    def test_06_external_id_unique(self):
        self.tx.external_id = "EXT1"
        with self.assertRaises(Exception):
            self.env["qonto.transaction"].create({
                "name": "QTO-002", "connection_id": self.conn.id,
                "label": "Dup", "amount": 1.0, "external_id": "EXT1",
            })

    def test_07_create_default_name(self):
        tx = self.env["qonto.transaction"].create({
            "connection_id": self.conn.id, "label": "Auto", "amount": 5.0,
        })
        self.assertTrue(tx.name and tx.name != "")

    def test_08_sync_creates_log(self):
        self.conn.action_activate()
        before = self.env["qonto.sync.log"].search_count([("connection_id", "=", self.conn.id)])
        self.conn.action_sync()
        after = self.env["qonto.sync.log"].search_count([("connection_id", "=", self.conn.id)])
        self.assertEqual(after, before + 1)
