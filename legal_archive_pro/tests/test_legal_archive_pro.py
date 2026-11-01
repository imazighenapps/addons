# -*- coding: utf-8 -*-
import base64
import hashlib
import uuid
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged

GENESIS = "0" * 64


@tagged("post_install", "-at_install")
class TestLegalArchivePro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.context_today(cls.env["archive.document"])
        cls.partner = cls.env["res.partner"].create({
            "name": "LegalArchivePro Test Counterparty",
        })

    def _stamp(self):
        """Build a hermetic PDF payload and its base64 encoding."""
        raw = b"%PDF-1.4 " + uuid.uuid4().hex.encode("ascii")
        # Odoo 20 Binary fields accept a base64 string, not raw bytes.
        return raw, base64.b64encode(raw).decode("ascii")

    def _document(self, **kwargs):
        values = {
            "name": "Invoice ACME 2026-001",
            "document_type": "invoice",
            "partner_id": self.partner.id,
            "reference": "LAR-TEST-001",
            "document_date": date(2020, 1, 15),
            "retention_years": 1,
            "file_name": "invoice.pdf",
        }
        values.update(kwargs)
        return self.env["archive.document"].create(values)

    def test_01_seal_computes_the_sha256(self):
        raw, payload = self._stamp()
        document = self._document(
            reference="LAR-TEST-SEAL", file_data=payload)
        self.assertFalse(document.hash)
        self.assertTrue(document.action_seal())
        expected = hashlib.sha256(
            GENESIS.encode("utf-8") + raw).hexdigest()
        self.assertEqual(document.previous_hash, GENESIS)
        self.assertEqual(document.hash, expected)

    def test_02_verify_succeeds_on_unmodified_file(self):
        raw, payload = self._stamp()
        document = self._document(
            reference="LAR-TEST-VER", file_data=payload)
        document.action_seal()
        self.assertTrue(document.action_verify())
        verified = document.log_ids.filtered(
            lambda log: log.action == "verified")
        self.assertEqual(len(verified), 1)
        self.assertIn("succeeded", verified.note)

    def test_03_verify_fails_after_file_modification(self):
        raw, payload = self._stamp()
        document = self._document(
            reference="LAR-TEST-MOD", file_data=payload)
        document.action_seal()
        other_raw, other_payload = self._stamp()
        document.write({"file_data": other_payload})
        # Do NOT use assertRaises here: Odoo 20 wraps it in a savepoint
        # that is rolled back on the expected exception, which would wipe
        # the "failed" verification log we want to inspect afterwards.
        captured = None
        try:
            document.action_verify()
        except UserError:
            captured = True
        self.assertTrue(captured)
        mismatch = self.env["archive.log"].search([
            ("document_id", "=", document.id),
            ("action", "=", "verified"),
        ])
        self.assertIn("failed", mismatch.note)
        # Restoring the original bytes makes the verification pass again.
        document.write({"file_data": payload})
        self.assertTrue(document.action_verify())

    def test_04_previous_hash_chains_documents(self):
        raw1, payload1 = self._stamp()
        first = self._document(
            reference="LAR-TEST-CHA1", file_data=payload1)
        first.action_seal()
        raw2, payload2 = self._stamp()
        second = self._document(
            reference="LAR-TEST-CHA2", file_data=payload2)
        second.action_seal()
        self.assertEqual(second.previous_hash, first.hash)
        expected = hashlib.sha256(
            first.hash.encode("utf-8") + raw2).hexdigest()
        self.assertEqual(second.hash, expected)

    def test_05_expiry_computed_from_document_date(self):
        document = self._document(reference="LAR-TEST-EXPIRY")
        self.assertEqual(
            document.expiry_date,
            date(2020, 1, 15) + timedelta(days=365))
        document.write({"retention_years": 5})
        self.assertEqual(
            document.expiry_date,
            date(2020, 1, 15) + timedelta(days=1825))

    def test_06_purge_refused_before_expiry_then_allowed(self):
        raw, payload = self._stamp()
        document = self._document(
            reference="LAR-TEST-PURGE",
            document_date=self.today,
            retention_years=10,
            file_data=payload,
            name="Bill Supplier 2026-045",
        )
        self.assertGreater(document.expiry_date, self.today)
        document.action_archive()
        with self.assertRaises(UserError):
            document.action_purge()
        self.assertTrue(document.file_data)
        self.assertEqual(document.state, "archived")
        document.write({"document_date": date(2014, 1, 15)})
        self.assertTrue(document.action_purge())
        self.assertEqual(document.state, "purged")
        self.assertFalse(document._decode_file())
        self.assertTrue(self.env["archive.log"].search([
            ("document_id", "=", document.id),
            ("action", "=", "purged"),
        ]))
        with self.assertRaises(UserError):
            document.action_verify()

    def test_07_every_action_writes_a_log_line(self):
        raw, payload = self._stamp()
        document = self._document(
            reference="LAR-TEST-LOG", file_data=payload)
        created = document.log_ids.filtered(
            lambda log: log.action == "created")
        self.assertEqual(len(created), 1)
        self.assertTrue(created.user_id)
        document.action_seal()
        document.action_archive()
        self.assertTrue(document.log_ids.filtered(
            lambda log: log.action == "sealed"))
        self.assertTrue(document.log_ids.filtered(
            lambda log: log.action == "archived"))

    def test_08_reference_unique_per_company(self):
        self._document(reference="LAR-TEST-DUP")
        with self.assertRaises(ValidationError):
            self._document(
                reference="LAR-TEST-DUP",
                name="Invoice ACME 2026-002",
            )
        with self.assertRaises(ValidationError):
            self.env["archive.document"].create([
                {"name": "Batch One", "reference": "LAR-TEST-BATCH"},
                {"name": "Batch Two", "reference": "LAR-TEST-BATCH"},
            ])
