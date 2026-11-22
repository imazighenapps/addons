# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestMandateLifecycle(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Partenaire Mandat"})

    def test_create_and_lifecycle(self):
        m = self.env["mandate.lifecycle"].create({
            "name": "M-001",
            "partner_id": self.partner.id,
            "iban": "FR7630006000011234567890189",
            "signature_date": date.today(),
        })
        self.assertEqual(m.state, "new")
        m.action_activate()
        self.assertEqual(m.state, "active")
        m.action_revoke()
        self.assertEqual(m.state, "revoked")

    def test_rib_versioning(self):
        m = self.env["mandate.lifecycle"].create({
            "name": "M-002",
            "partner_id": self.partner.id,
            "iban": "FR7630006000011234567890189",
        })
        m.action_change_rib("DE89370400440532013000", "COBADEFFXXX", "Changement banque")
        self.assertEqual(len(m.rib_history_ids), 1)
        self.assertEqual(m.iban, "DE89370400440532013000")

    def test_expiry_cron(self):
        m = self.env["mandate.lifecycle"].create({
            "name": "M-003",
            "partner_id": self.partner.id,
            "iban": "FR7630006000011234567890189",
            "state": "active",
            "expiry_date": date.today() - timedelta(days=1),
        })
        self.env["mandate.lifecycle"]._cron_check_expiry()
        self.assertEqual(m.state, "expired")
