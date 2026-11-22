# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged
from odoo import Command


@tagged("post_install", "-at_install")
class TestBankReconcileAssist(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.bank_journal = cls.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", cls.company.id)], limit=1)
        if not cls.bank_journal:
            cls.bank_journal = cls.env["account.journal"].create({
                "name": "Banque Test", "code": "BNKT", "type": "bank",
                "company_id": cls.company.id,
            })
        cls.partner = cls.env["res.partner"].create({"name": "Client Rappro"})
        cls.account_recv = cls.env["account.account"].search([
            ("account_type", "=", "asset_receivable"),
            ("company_ids", "in", [cls.company.id]),
        ], limit=1)

    def test_rule_create_and_match(self):
        rule = self.env["bank.reconcile.rule"].create({
            "name": "Règle libellé",
            "label_contains": "FACTURE",
            "amount_tolerance": 1.0,
            "tolerance_type": "fixed",
        })
        self.assertTrue(rule.active)
        self.assertTrue(rule.amount_in_tolerance(100.0, 100.5))
        self.assertFalse(rule.amount_in_tolerance(100.0, 102.0))

    def test_wizard_requires_lines(self):
        wiz = self.env["bank.reconcile.assist.wizard"].create({
            "journal_id": self.bank_journal.id,
            "date_from": date(2030, 1, 1),
            "date_to": date(2030, 1, 31),
        })
        # Période vide : doit lever une erreur utilisateur explicite
        from odoo.exceptions import UserError
        with self.assertRaises(UserError):
            wiz.action_compute()

    def test_progress_notification(self):
        wiz = self.env["bank.reconcile.assist.wizard"].create({
            "journal_id": self.bank_journal.id,
            "date_from": date.today().replace(day=1),
            "date_to": date.today(),
        })
        res = wiz.action_progress_report()
        self.assertEqual(res["type"], "ir.actions.client")
        self.assertIn("message", res["params"])
