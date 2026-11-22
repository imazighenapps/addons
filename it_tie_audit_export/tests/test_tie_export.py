# -*- coding: utf-8 -*-
"""Tests fonctionnels de l'export TIE Italie."""
import base64
from datetime import date

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTieExport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        if not cls.company.vat:
            cls.company.vat = "IT12345678901"
        cls.journal = cls.env["account.journal"].create({
            "name": "Journal TIE", "code": "TIEJ", "type": "general",
            "company_id": cls.company.id,
        })
        cls.acc_rev = cls.env["account.account"].create({
            "name": "Ricavi TIE", "code": "801000",
            "account_type": "income"})
        cls.acc_cash = cls.env["account.account"].create({
            "name": "Cassa TIE", "code": "501000",
            "account_type": "asset_cash"})
        cls.partner = cls.env["res.partner"].create({
            "name": "Cliente TIE", "vat": "IT98765432101"})
        move = cls.env["account.move"].create({
            "journal_id": cls.journal.id,
            "date": date(2025, 4, 10),
            "move_type": "entry",
            "line_ids": [
                Command.create({"account_id": cls.acc_cash.id,
                                "partner_id": cls.partner.id,
                                "debit": 500.0, "credit": 0.0}),
                Command.create({"account_id": cls.acc_rev.id,
                                "partner_id": cls.partner.id,
                                "debit": 0.0, "credit": 500.0}),
            ],
        })
        move.action_post()

    def _export(self, **kw):
        kw.setdefault("company_id", self.company.id)
        kw.setdefault("date_from", date(2025, 4, 1))
        kw.setdefault("date_to", date(2025, 4, 30))
        kw.setdefault("journal_ids", [Command.set([self.journal.id])])
        return self.env["tie.export"].create(kw)

    def _decode(self, export):
        data = bytes(export.file_data or b"")
        # v20 may return decoded content; base64 text starts with alnum (e.g. 77u/ for BOM+TIE)
        if data.startswith(b"TIE;") or data.startswith(b"\xef\xbb\xbf"):
            return data.decode("utf-8-sig")
        try:
            return base64.b64decode(data).decode("utf-8-sig")
        except Exception:
            return data.decode("utf-8-sig")

    def test_mapping_required_error(self):
        with self.assertRaises(UserError):
            self._export().action_generate()

    def test_generation_with_mapping(self):
        self.env["tie.registry.map"].create({
            "company_id": self.company.id,
            "registry_code": "generale",
            "journal_ids": [Command.set([self.journal.id])],
        })
        export = self._export()
        export.action_generate()
        self.assertEqual(export.state, "generated")
        self.assertTrue(export.file_name.startswith("TIE_IT12345678901_"))
        self.assertEqual(export.record_count, 2)
        self.assertAlmostEqual(export.total_debit, 500.0, places=2)
        self.assertAlmostEqual(export.total_credit, 500.0, places=2)
        rows = self._decode(export).strip().split("\r\n")
        self.assertEqual(rows[0].split(";")[0], "TIE")
        self.assertEqual(rows[0].split(";")[1], "IT12345678901")
        self.assertEqual(rows[1].split(";")[0], "RegistroFiscale")
        self.assertEqual(len(rows[1].split(";")), 12)
        data = rows[2].split(";")
        self.assertEqual(data[0], "generale")
        self.assertEqual(data[1], "TIEJ")
        self.assertEqual(data[2], "20250410")
        self.assertIn(data[6], ("D", "A"))
        self.assertIn(",", data[7])
        tot = rows[-1].split(";")
        self.assertEqual(tot[0], "TOT")
        self.assertEqual(tot[1], "2")
        self.assertEqual(tot[2], "500,00")
        self.assertEqual(tot[3], "500,00")

    def test_allow_unmapped(self):
        export = self._export(allow_unmapped=True)
        export.action_generate()
        rows = self._decode(export).strip().split("\r\n")
        self.assertEqual(rows[2].split(";")[0], "NON_MAPPATO")
        self.assertIn("TIEJ", export.warnings)

    def test_completeness_report(self):
        export = self._export()
        export.action_check_completeness()
        self.assertIn("TIEJ", export.warnings)
        self.env["tie.registry.map"].create({
            "company_id": self.company.id,
            "registry_code": "generale",
            "journal_ids": [Command.set([self.journal.id])],
        })
        export.action_check_completeness()
        self.assertIn("Complétude OK", export.warnings)

    def test_deposit_log(self):
        self.env["tie.registry.map"].create({
            "company_id": self.company.id,
            "registry_code": "generale",
            "journal_ids": [Command.set([self.journal.id])],
        })
        export = self._export()
        with self.assertRaises(UserError):
            export.action_mark_deposited()
        export.action_generate()
        export.action_mark_deposited()
        self.assertEqual(export.state, "deposited")
        self.assertEqual(export.deposited_by, self.env.user)
        self.assertTrue(export.deposited_on)

    def test_unique_registry_per_company(self):
        self.env["tie.registry.map"].search([
            ("company_id", "=", self.company.id),
            ("registry_code", "=", "generale"),
        ]).unlink()
        self.env["tie.registry.map"].create({
            "company_id": self.company.id,
            "registry_code": "generale",
            "journal_ids": [Command.set([self.journal.id])],
        })
        with self.assertRaises(Exception):
            self.env["tie.registry.map"].create({
                "company_id": self.company.id,
                "registry_code": "generale",
                "journal_ids": [Command.set([self.journal.id])],
            })

    def test_date_order_constraint(self):
        with self.assertRaises(ValidationError):
            self._export(date_from=date(2025, 4, 30),
                         date_to=date(2025, 4, 1))
