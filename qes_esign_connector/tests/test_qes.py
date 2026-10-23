# -*- coding: utf-8 -*-
import base64
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestQes(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider = cls.env.ref("qes_esign_connector.provider_demo")
        cls.account = cls.env["qes.account"].create({
            "name": "Demo Account", "provider_id": cls.provider.id, "environment": "preprod",
        })
        cls.doc_bytes = b"%PDF-1.4 demo contract for tests"
        cls.attachment = cls.env["ir.attachment"].create({
            "name": "contract.pdf", "raw": base64.b64encode(cls.doc_bytes),
            "mimetype": "application/pdf",
        })

    def _make_envelope(self, levels=("qes", "ses")):
        env = self.env["qes.envelope"].create({
            "name": "NDA Demo", "account_id": self.account.id,
        })
        parts = []
        for i, lvl in enumerate(levels):
            parts.append((0, 0, {
                "name": "Signer %d" % i, "email": "signer%d@demo.test" % i,
                "role": "signer", "sequence": (i + 1) * 10, "required_level": lvl,
            }))
        env.write({"participant_ids": parts})
        env.write({"document_ids": [(0, 0, {
            "name": "NDA", "attachment_id": self.attachment.id, "pades_level": "b-t",
        })]})
        return env

    def test_01_providers_seeded(self):
        self.assertEqual(len(self.env["qes.provider"].search([])), 3)

    def test_02_prepare_requires_content(self):
        env = self.env["qes.envelope"].create({
            "name": "Empty", "account_id": self.account.id})
        with self.assertRaises(UserError):
            env.action_prepare()

    def test_03_demo_full_flow(self):
        env = self._make_envelope()
        env.action_prepare()
        self.assertEqual(env.state, "ready")
        env.action_start()
        self.assertEqual(env.state, "sent")
        self.assertTrue(env.provider_tx_id.startswith("DEMO-"))
        env.participant_ids[0].action_demo_sign()
        self.assertEqual(env.state, "partial")
        env.participant_ids[1].action_demo_sign()
        self.assertEqual(env.state, "signed")
        self.assertEqual(env.participant_ids[0].obtained_level, "qes")
        self.assertTrue(env.signed_pdf_id)
        hashes = [e.event_hash for e in env.event_ids]
        self.assertEqual(len(set(hashes)), len(hashes))
        self.assertTrue(all(hashes))
        env.action_fetch_evidence()
        self.assertIn("DEMO-", env.validation_report)

    def test_04_double_sign_blocked(self):
        env = self._make_envelope(levels=("ses",))
        env.action_prepare()
        env.action_start()
        env.participant_ids.action_demo_sign()
        with self.assertRaises(UserError):
            env.participant_ids.action_demo_sign()

    def test_05_document_hash(self):
        env = self._make_envelope()
        doc = env.document_ids
        import hashlib
        self.assertEqual(doc.sha256_origin, hashlib.sha256(self.doc_bytes).hexdigest())
