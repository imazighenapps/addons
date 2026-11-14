# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMondayBridge(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["monday.connection"].create({
            "name": "Coffee Conn 1",
            "api_key": "demo-key",
            "endpoint": "https://example.com/api",
        })
        cls.rec = cls.env["monday.record"].create({
            "name": "Rec 1",
            "connection_id": cls.conn.id,
            "external_ref": "EXT-1",
        })

    def test_01_connection_activate(self):
        self.conn.action_activate()
        self.assertEqual(self.conn.state, "active")

    def test_02_connection_activate_requires_key(self):
        c = self.env["monday.connection"].create({"name": "NoKey", "endpoint": "https://example.com"})
        with self.assertRaises(UserError):
            c.action_activate()

    def test_03_endpoint_validation(self):
        with self.assertRaises(ValidationError):
            self.env["monday.connection"].create({"name": "Bad", "endpoint": "ftp://x"})

    def test_04_record_prepare_requires_active(self):
        with self.assertRaises(UserError):
            self.rec.action_prepare()

    def test_05_record_flow(self):
        self.conn.action_activate()
        self.rec.action_prepare()
        self.assertEqual(self.rec.state, "ready")
        self.rec.action_run()
        self.assertEqual(self.rec.state, "done")
        self.assertTrue(self.rec.processed_at)

    def test_06_record_reset_blocked_when_done(self):
        self.conn.action_activate()
        self.rec.action_prepare()
        self.rec.action_run()
        with self.assertRaises(UserError):
            self.rec.action_reset()

    def test_07_mark_error(self):
        self.conn.action_activate()
        self.rec.action_prepare()
        self.rec.action_mark_error()
        self.assertEqual(self.rec.state, "error")

    def test_08_log_created_on_run(self):
        self.conn.action_activate()
        self.rec.action_prepare()
        self.rec.action_run()
        self.assertTrue(self.rec.log_ids)
