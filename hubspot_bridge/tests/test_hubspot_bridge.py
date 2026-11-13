# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHubspotBridge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["hubspot.connection"].create({"name": "HS", "token_ref": "tok"})
        cls.partner = cls.env["res.partner"].create({"name": "P"})
        cls.lead = cls.env["crm.lead"].create({"name": "Deal"})
        cls.sync = cls.env["hubspot.sync"].create({
            "name": "HS-1", "connection_id": cls.conn.id, "object_type": "contact",
            "partner_id": cls.partner.id,
        })

    def test_01_activate(self):
        c = self.env["hubspot.connection"].create({"name": "X"})
        with self.assertRaises(UserError): c.action_activate()

    def test_02_contact_requires_partner(self):
        with self.assertRaises(ValidationError):
            self.env["hubspot.sync"].create({"name": "HS-2", "connection_id": self.conn.id, "object_type": "contact"})

    def test_03_deal_requires_lead(self):
        with self.assertRaises(ValidationError):
            self.env["hubspot.sync"].create({"name": "HS-3", "connection_id": self.conn.id, "object_type": "deal"})

    def test_04_prepare_sync(self):
        self.conn.action_activate()
        self.sync.action_prepare(); self.sync.action_sync()
        self.assertEqual(self.sync.state, "synced")
        self.assertTrue(self.sync.external_id)

    def test_05_sync_requires_ready(self):
        self.conn.action_activate()
        with self.assertRaises(UserError): self.sync.action_sync()

    def test_06_sync_requires_active(self):
        self.sync.action_prepare()
        with self.assertRaises(UserError): self.sync.action_sync()

    def test_07_reset(self):
        self.conn.action_activate(); self.sync.action_prepare(); self.sync.action_sync()
        self.sync.action_reset(); self.assertEqual(self.sync.state, "draft")

    def test_08_deal_sync(self):
        self.conn.action_activate()
        s = self.env["hubspot.sync"].create({
            "name": "HS-D", "connection_id": self.conn.id, "object_type": "deal", "lead_id": self.lead.id,
        })
        s.action_prepare(); s.action_sync(); self.assertEqual(s.state, "synced")
