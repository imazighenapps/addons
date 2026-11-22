# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError

from odoo.addons.sepa_credit_transfer.models.sct_batch import _valid_iban, _clean_iban


@tagged("post_install", "-at_install")
class TestSctBatch(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.bank_journal = cls.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", cls.company.id)], limit=1)
        if not cls.bank_journal:
            cls.bank_journal = cls.env["account.journal"].create({
                "name": "Banque", "code": "BNK1", "type": "bank", "company_id": cls.company.id,
            })

    def test_iban_helpers(self):
        self.assertEqual(_clean_iban("fr76 3000 6000 0112 3456 7890 189"), "FR7630006000011234567890189")
        self.assertTrue(_valid_iban("FR7630006000011234567890189"))
        self.assertFalse(_valid_iban("FR7630006000011234567890180"))
        self.assertFalse(_valid_iban("INVALID"))

    def test_batch_create_and_empty_generate(self):
        batch = self.env["sct.batch"].create({
            "journal_id": self.bank_journal.id,
        })
        self.assertEqual(batch.state, "draft")
        with self.assertRaises(UserError):
            batch.action_generate()
