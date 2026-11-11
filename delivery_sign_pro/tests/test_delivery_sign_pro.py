# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSignDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "SignDesk Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "SignDesk Customer Alpha"})
        cls.partner_b = cls.env["res.partner"].create({
            "name": "SignDesk Customer Beta"})

    def _proof(self, **values):
        defaults = {
            "name": "SignDesk DEL-2026-001",
            "partner_id": self.partner.id,
            "delivery_date": date(2026, 11, 4),
            "recipient_name": "SignDesk Recipient A",
            "signature_ok": True,
            "photo_ok": True,
        }
        defaults.update(values)
        return self.env["delivery.proof"].create(defaults)

    def test_01_proof_defaults(self):
        proof = self._proof(name="SignDesk DEL-2026-002", signature_ok=False,
                            photo_ok=False, recipient_name=False)
        self.assertEqual(proof.state, "pending")
        self.assertEqual(proof.company_id, self.env.company)
        self.assertFalse(proof.proof_complete)
        self.assertFalse(proof.signed_on)

    def test_02_proof_complete_flag(self):
        proof = self._proof(name="SignDesk DEL-2026-003")
        self.assertTrue(proof.proof_complete)
        proof.write({"photo_ok": False})
        self.assertFalse(proof.proof_complete)

    def test_03_mark_signed_records_date(self):
        proof = self._proof(name="SignDesk DEL-2026-004")
        self.assertTrue(proof.action_mark_signed())
        self.assertEqual(proof.state, "signed")
        self.assertTrue(proof.signed_on)

    def test_04_signature_required_before_signing(self):
        proof = self._proof(name="SignDesk DEL-2026-005", signature_ok=False)
        with self.assertRaises(ValidationError):
            proof.action_mark_signed()

    def test_05_recipient_required_before_signing(self):
        proof = self._proof(name="SignDesk DEL-2026-006",
                            recipient_name=False)
        with self.assertRaises(ValidationError):
            proof.action_mark_signed()

    def test_06_double_sign_is_refused(self):
        proof = self._proof(name="SignDesk DEL-2026-007")
        proof.action_mark_signed()
        with self.assertRaises(ValidationError):
            proof.action_mark_signed()

    def test_07_signed_on_before_delivery_is_refused(self):
        with self.assertRaises(ValidationError):
            self._proof(name="SignDesk DEL-2026-008",
                        delivery_date=date(2026, 11, 10),
                        signed_on=date(2026, 11, 9))

    def test_08_missing_evidence_filters(self):
        missing_sig = self._proof(name="SignDesk DEL-2026-009",
                                  signature_ok=False, photo_ok=True)
        missing_photo = self._proof(name="SignDesk DEL-2026-010",
                                    partner_id=self.partner_b.id,
                                    signature_ok=True, photo_ok=False)
        found_sig = self.env["delivery.proof"].search([
            ("signature_ok", "=", False), ("state", "=", "pending")])
        found_photo = self.env["delivery.proof"].search([
            ("photo_ok", "=", False), ("state", "=", "pending")])
        self.assertIn(missing_sig, found_sig)
        self.assertIn(missing_photo, found_photo)
        self.assertNotIn(missing_photo, found_sig)

    def test_09_company_isolation(self):
        foreign_partner = self.env["res.partner"].with_company(
            self.other_company).sudo().create({
                "name": "SignDesk Foreign Customer",
                "company_id": self.other_company.id,
            })
        foreign = self.env["delivery.proof"].with_company(
            self.other_company).sudo().create({
                "name": "SignDesk Foreign DEL",
                "partner_id": foreign_partner.id,
                "delivery_date": date(2026, 11, 15),
                "company_id": self.other_company.id,
            })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._proof(name="SignDesk Local DEL")
        self.assertNotEqual(local.company_id, foreign.company_id)
