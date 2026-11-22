# -*- coding: utf-8 -*-
from datetime import date
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError

from odoo.addons.sepa_direct_debit.models.sdd_mandate import _valid_iban


@tagged("post_install", "-at_install")
class TestSdd(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create({"name": "Débiteur SDD"})
        bank_field = "acc_number" if "acc_number" in cls.env["res.partner.bank"]._fields else "account_number"
        cls.bank = cls.env["res.partner.bank"].create({
            bank_field: "FR7630006000011234567890189",
            "partner_id": cls.partner.id,
        })
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", cls.company.id)], limit=1)
        if not cls.journal:
            cls.journal = cls.env["account.journal"].create({
                "name": "Banque", "code": "BNK", "type": "bank", "company_id": cls.company.id,
            })

    def test_iban_helper(self):
        self.assertTrue(_valid_iban("FR7630006000011234567890189"))

    def test_mandate_lifecycle(self):
        mandate = self.env["sdd.mandate"].create({
            "name": "MAND-001",
            "partner_id": self.partner.id,
            "partner_bank_id": self.bank.id,
            "signature_date": date.today(),
        })
        self.assertEqual(mandate.state, "draft")
        mandate.action_activate()
        self.assertEqual(mandate.state, "active")
        mandate.consume_sequence()
        self.assertEqual(mandate.sequence_type, "RCUR")

    def test_batch_create(self):
        mandate = self.env["sdd.mandate"].create({
            "name": "MAND-002",
            "partner_id": self.partner.id,
            "partner_bank_id": self.bank.id,
            "signature_date": date.today(),
            "state": "active",
        })
        batch = self.env["sdd.batch"].create({
            "journal_id": self.journal.id,
            "creditor_identifier": "FR00ZZZ123456",
            "line_ids": [(0, 0, {"name": "L1", "mandate_id": mandate.id, "amount": 10.0})],
        })
        self.assertEqual(batch.nb_txs, 1)
        self.assertAlmostEqual(batch.ctrl_sum, 10.0)
