# -*- coding: utf-8 -*-
"""Tests fonctionnels du validateur FEC."""
import base64
from datetime import date

from odoo import Command
from odoo.tests import TransactionCase, tagged

HEADER = "\t".join([
    "CodeJournal", "JournalLib", "EcritureNum", "EcritureDate",
    "CompNumMvt", "CompPieceNum", "AccountNum", "AccountLib",
    "CompAuxNum", "CompAuxLib", "PieceRef", "PieceDate", "EcritureLib",
    "Debit", "Credit", "EcritureLet", "DateLet", "ValidDate"])


def _file(lines):
    content = HEADER + "\r\n" + "\r\n".join(lines) + "\r\n"
    return base64.b64encode(content.encode("cp1252")).decode("ascii")


def _line(journal, num, date, piece, account, lib, debit, credit,
          valid_date="20250201", extra_cols=None):
    sep = "\t"
    values = [journal, "Journal %s" % journal, num, date, num, piece,
              account, lib, "", "", piece, date, "Libellé écriture",
              debit, credit, "", "", valid_date]
    if extra_cols:
        values += extra_cols
    return sep.join(values)


@tagged("post_install", "-at_install")
class TestFecValidator(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.acc_rev = cls.env["account.account"].create({
            "name": "Ventes FECV", "code": "700001",
            "account_type": "income"})
        cls.acc_cash = cls.env["account.account"].create({
            "name": "Caisse FECV", "code": "580001",
            "account_type": "asset_cash"})

    def _validate(self, content_b64, name="FEC test"):
        validation = self.env["fec.validation"].create({
            "name": name,
            "source_file": content_b64,
            "file_name": "FEC.txt",
        })
        validation.action_validate()
        return validation

    def test_valid_file(self):
        lines = [
            _line("VT", "1", "20250115", "FAC-1", "700000", "Ventes",
                  "0,00", "1000,00"),
            _line("VT", "2", "20250120", "FAC-2", "580000", "Caisse",
                  "1000,00", "0,00"),
            _line("VT", "3", "20250121", "FAC-3", "580000", "Caisse",
                  "0,00", "1000,00"),
        ]
        # 3 lignes : débit 1000 / crédit 1000+1000? Non : équilibre à 2000/2000
        lines.append(_line("VT", "4", "20250122", "FAC-4", "700000",
                           "Ventes", "1000,00", "0,00"))
        v = self._validate(_file(lines))
        self.assertEqual(v.state, "validated")
        self.assertEqual(v.error_count, 0)
        self.assertEqual(v.record_count, 4)
        self.assertAlmostEqual(v.total_debit, 2000.0, places=2)
        self.assertAlmostEqual(v.total_credit, 2000.0, places=2)
        self.assertEqual(v.detected_separator, "tabulation")

    def test_balance_gap_detected(self):
        lines = [
            _line("VT", "1", "20250115", "FAC-1", "700000", "Ventes",
                  "0,00", "1000,00"),
        ]
        v = self._validate(_file(lines))
        self.assertEqual(v.state, "with_errors")
        balance = v.line_ids.filtered(lambda l: l.code == "balance")
        self.assertEqual(len(balance), 1)
        self.assertEqual(balance.severity, "error")
        self.assertIn("déséquilibrée", balance.message)

    def test_length_and_date_errors(self):
        lines = [
            _line("VT", "1", "20259915", "FAC-1", "700000",
                  "L" * 80, "0,00", "1000,00"),
        ]
        v = self._validate(_file(lines))
        length_errors = v.line_ids.filtered(
            lambda l: l.code == "length" and
            l.field_name == "AccountLib")
        date_errors = v.line_ids.filtered(
            lambda l: l.field_name == "EcritureDate")
        self.assertEqual(len(length_errors), 1)
        self.assertEqual(length_errors.line_number, 2)
        self.assertEqual(len(date_errors), 1)

    def test_numeric_and_sequence_errors(self):
        lines = [
            _line("VT", "A1", "20250115", "FAC-1", "70X00", "Ventes",
                  "0,00", "1000,00"),
            _line("VT", "2", "20250116", "FAC-2", "580000", "Caisse",
                  "0,00", "1000,00"),
            _line("VT", "1", "20250117", "FAC-3", "580000", "Caisse",
                  "0,00", "1000,00"),
        ]
        v = self._validate(_file(lines))
        num_err = v.line_ids.filtered(
            lambda l: l.field_name == "EcritureNum")
        account_err = v.line_ids.filtered(
            lambda l: l.field_name == "AccountNum")
        seq_err = v.line_ids.filtered(
            lambda l: l.code == "sequence" and l.line_number == 4)
        self.assertGreaterEqual(len(num_err), 1)
        self.assertGreaterEqual(len(account_err), 1)
        self.assertGreaterEqual(len(seq_err), 1)

    def test_move_reference_pointing(self):
        """Les anomalies pointent vers la pièce, et le lien ouvre l'écriture."""
        journal = self.env["account.journal"].create({
            "name": "Journal Test", "code": "JTST", "type": "general",
            "company_id": self.env.company.id})
        move = self.env["account.move"].create({
            "journal_id": journal.id,
            "date": date(2025, 1, 15),
            "move_type": "entry",
            "line_ids": [
                Command.create({"account_id": self.acc_cash.id,
                                "debit": 1000.0, "credit": 0.0}),
                Command.create({"account_id": self.acc_rev.id,
                                "debit": 0.0, "credit": 1000.0}),
            ],
        })
        move.action_post()
        lines = [
            _line("VT", "1", "20250115", move.name, "700000", "Ventes",
                  "0,00", "1000,00"),
        ]
        v = self._validate(_file(lines))
        balance = v.line_ids.filtered(lambda l: l.code == "balance")
        self.assertTrue(balance)
        self.assertEqual(balance[0].move_ref, move.name)
        action = balance[0].action_open_move()
        self.assertEqual(action.get("res_model"), "account.move")
        self.assertEqual(action.get("res_id"), move.id)

    def test_missing_header_field(self):
        # En-tête sans EcritureLib
        bad_header = HEADER.replace("EcritureLib\t", "")
        content = bad_header + "\r\n" + _line(
            "VT", "1", "20250115", "FAC-1", "700000", "Ventes",
            "0,00", "1000,00") + "\r\n"
        v = self._validate(base64.b64encode(
            content.encode("cp1252")).decode("ascii"))
        missing = v.line_ids.filtered(
            lambda l: l.code == "missing")
        self.assertGreaterEqual(len(missing), 1)
        self.assertIn("EcritureLib", v.line_ids.mapped("field_name"))
