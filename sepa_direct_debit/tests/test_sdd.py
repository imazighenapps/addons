# -*- coding: utf-8 -*-
import base64
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSepaDirectDebit(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create({
            "name": "Test Debtor",
            "email": "debtor@example.com",
        })
        cls.iban_field = "acc_number" if "acc_number" in cls.env["res.partner.bank"]._fields else "account_number"
        cls.bank = cls.env["res.partner.bank"].create({
            cls.iban_field: "FR7630006000011234567890189",
            "partner_id": cls.partner.id,
            "company_id": cls.company.id,
        })
        cls.journal = cls.env["account.journal"].search([("type", "=", "bank"), ("company_id", "=", cls.company.id)], limit=1)
        if not cls.journal:
            cls.journal = cls.env["account.journal"].create({
                "name": "Bank", "type": "bank", "code": "BNK1", "company_id": cls.company.id,
            })
        valid_iban = "FR7630006000011234567890189"
        if not cls.journal.bank_account_id or (getattr(cls.journal.bank_account_id, cls.iban_field, "") or "").replace(" ", "") != valid_iban:
            comp_bank = cls.env["res.partner.bank"].search([
                (cls.iban_field, "=", valid_iban),
                ("partner_id", "=", cls.company.partner_id.id),
            ], limit=1)
            if not comp_bank:
                comp_bank = cls.env["res.partner.bank"].create({
                    cls.iban_field: valid_iban,
                    "partner_id": cls.company.partner_id.id,
                    "company_id": cls.company.id,
                })
            cls.journal.bank_account_id = comp_bank.id
        cls.mandate = cls.env["sdd.mandate"].create({
            "partner_id": cls.partner.id,
            "partner_bank_id": cls.bank.id,
            "company_id": cls.company.id,
            "scheme": "CORE",
            "signature_date": fields.Date.today(),
        })

    def test_mandate_activation(self):
        self.assertEqual(self.mandate.state, "draft")
        self.mandate.action_activate()
        self.assertEqual(self.mandate.state, "active")
        self.mandate.action_suspend()
        self.assertEqual(self.mandate.state, "suspended")
        self.mandate.action_activate()
        self.assertEqual(self.mandate.state, "active")

    def test_invalid_iban_raises(self):
        iban_field = "acc_number" if "acc_number" in self.env["res.partner.bank"]._fields else "account_number"
        bad_bank = self.env["res.partner.bank"].create({
            iban_field: "FR00INVALIDIBAN12345",
            "partner_id": self.partner.id,
            "company_id": self.company.id,
        })
        with self.assertRaises(ValidationError):
            self.env["sdd.mandate"].create({
                "partner_id": self.partner.id,
                "partner_bank_id": bad_bank.id,
                "company_id": self.company.id,
                "scheme": "CORE",
                "signature_date": fields.Date.today(),
            })

    def test_batch_generation_creates_pain008(self):
        self.mandate.action_activate()
        batch = self.env["sdd.batch"].create({
            "company_id": self.company.id,
            "journal_id": self.journal.id,
            "creditor_identifier": "FR00ZZZ000001",
            "scheme": "CORE",
            "sequence_type": "FRST",
            "collection_date": fields.Date.today(),
            "line_ids": [(0, 0, {
                "name": "INV/2026/0001",
                "mandate_id": self.mandate.id,
                "amount": 150.0,
                "communication": "Invoice INV/2026/0001",
            })],
        })
        batch.action_generate()
        self.assertEqual(batch.state, "generated")
        self.assertTrue(batch.file_data)
        fd = batch.file_data
        raw = fd.content if hasattr(fd, "content") else base64.b64decode(fd)
        xml = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
        self.assertIn("pain.008.001.02", xml)
        self.assertIn("FR7630006000011234567890189", xml.replace(" ", ""))
        self.assertIn("150.00", xml)

    def test_batch_workflow(self):
        self.mandate.action_activate()
        batch = self.env["sdd.batch"].create({
            "company_id": self.company.id,
            "journal_id": self.journal.id,
            "creditor_identifier": "FR00ZZZ000001",
            "scheme": "CORE",
            "sequence_type": "FRST",
            "collection_date": fields.Date.today(),
            "line_ids": [(0, 0, {
                "name": "INV/2026/0001",
                "mandate_id": self.mandate.id,
                "amount": 100.0,
                "communication": "INV/2026/0001",
            })],
        })
        batch.action_generate()
        self.assertEqual(batch.state, "generated")
        batch.action_mark_sent()
        self.assertEqual(batch.state, "sent")
        batch.action_mark_done()
        self.assertEqual(batch.state, "done")

    def test_batch_requires_lines(self):
        batch = self.env["sdd.batch"].create({
            "company_id": self.company.id,
            "journal_id": self.journal.id,
            "creditor_identifier": "FR00ZZZ000001",
            "scheme": "CORE",
            "sequence_type": "FRST",
            "collection_date": fields.Date.today(),
        })
        with self.assertRaises(Exception):
            batch.action_generate()

    def test_mandate_revoke_close(self):
        self.mandate.action_activate()
        self.mandate.action_revoke()
        self.assertEqual(self.mandate.state, "revoked")
