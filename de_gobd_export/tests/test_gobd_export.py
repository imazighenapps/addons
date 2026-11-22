# -*- coding: utf-8 -*-
"""Tests fonctionnels de l'export GoBD."""
import base64
import io
import zipfile
from datetime import date

from lxml import etree

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGobdExport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.journal = cls.env["account.journal"].create({
            "name": "Journal GoBD", "code": "GOBD", "type": "general",
            "company_id": cls.company.id,
        })
        cls.acc_rev = cls.env["account.account"].create({
            "name": "Umsatz GoBD", "code": "840000",
            "account_type": "income",
        })
        cls.acc_cash = cls.env["account.account"].create({
            "name": "Kasse GoBD", "code": "100000",
            "account_type": "asset_cash",
        })
        move = cls.env["account.move"].create({
            "journal_id": cls.journal.id,
            "date": date(2025, 5, 10),
            "move_type": "entry",
            "ref": "GOBD-1",
            "line_ids": [
                Command.create({"account_id": cls.acc_cash.id,
                                "debit": 500.0, "credit": 0.0,
                                "name": "Kasse"}),
                Command.create({"account_id": cls.acc_rev.id,
                                "debit": 0.0, "credit": 500.0,
                                "name": "Umsatz"}),
            ],
        })
        move.action_post()

    def _export(self, **kw):
        values = dict(
            company_id=self.company.id,
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
        )
        values.update(kw)
        return self.env["gobd.export"].create(values)

    def _zip(self, export):
        data = bytes(export.file_data or b"")
        if data[:2] != b"PK":
            data = base64.b64decode(data)
        return zipfile.ZipFile(io.BytesIO(data))

    def test_generation_zip_index_and_data(self):
        export = self._export(journal_ids=[Command.set([self.journal.id])])
        export.action_generate()
        self.assertEqual(export.state, "generated")
        self.assertTrue(export.file_name.endswith(".zip"))
        self.assertEqual(export.entry_count, 1)
        self.assertEqual(export.line_count, 2)
        self.assertAlmostEqual(export.total_debit, 500.0, places=2)
        self.assertAlmostEqual(export.total_credit, 500.0, places=2)
        self.assertIn("GoBD", export.protocol_note)

        zf = self._zip(export)
        names = set(zf.namelist())
        self.assertEqual(names, {"index.xml", "journal_entries.csv"})
        root = etree.fromstring(zf.read("index.xml"))
        self.assertEqual(root.tag, "DataSet")
        self.assertEqual(root.findtext(".//Table/URL"), "journal_entries.csv")
        cols = [e.text for e in root.findall(".//VariableColumn/Name")]
        self.assertIn("MoveName", cols)
        self.assertIn("Debit", cols)

        csv_text = zf.read("journal_entries.csv").decode("utf-8-sig")
        lines = csv_text.strip().split("\r\n")
        self.assertEqual(lines[0].split(";")[0], "MoveName")
        self.assertEqual(len(lines), 3)  # header + 2

    def test_empty_period_user_error(self):
        export = self._export(date_from=date(1999, 1, 1),
                              date_to=date(1999, 12, 31))
        with self.assertRaises(UserError):
            export.action_generate()

    def test_date_order_constraint(self):
        with self.assertRaises(ValidationError):
            self._export(date_from=date(2025, 12, 31),
                         date_to=date(2025, 1, 1))
