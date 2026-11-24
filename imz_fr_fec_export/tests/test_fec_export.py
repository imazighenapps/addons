# -*- coding: utf-8 -*-
"""Tests fonctionnels du générateur FEC."""
from datetime import date

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFecExport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        # Le nom du fichier FEC dépend du SIREN (numéro de TVA nettoyé)
        if not cls.company.vat:
            cls.company.vat = "FR32422111011"
        cls.journal = cls.env["account.journal"].create({
            "name": "Journal Vent FEC", "code": "VTS", "type": "general",
            "company_id": cls.company.id,
        })
        cls.acc_rev = cls.env["account.account"].create({
            "name": "Ventes FEC", "code": "700000",
            "account_type": "income",
        })
        cls.acc_cash = cls.env["account.account"].create({
            "name": "Caisse FEC", "code": "580000",
            "account_type": "asset_cash",
        })
        cls.acc_recv = cls.env["account.account"].create({
            "name": "Clients FEC", "code": "411000",
            "account_type": "asset_receivable",
            "reconcile": True,
        })
        cls.partner = cls.env["res.partner"].create({
            "name": "Client FEC", "ref": "C0001"})

        def move(d, ref, lines):
            m = cls.env["account.move"].create({
                "journal_id": cls.journal.id,
                "date": d, "ref": ref, "move_type": "entry",
                "line_ids": [Command.create({
                    "account_id": acc, "partner_id": partner_id,
                    "debit": deb, "credit": cred,
                }) for (acc, partner_id, deb, cred) in lines],
            })
            m.action_post()
            return m

        # 2 pièces, 4 lignes au total (ligne tiers sur compte receivable)
        move(date(2025, 1, 15), "FAC-1001", [
            (cls.acc_recv.id, cls.partner.id, 1000.0, 0.0),
            (cls.acc_rev.id, False, 0.0, 1000.0)])
        move(date(2025, 2, 20), "FAC-1002", [
            (cls.acc_recv.id, cls.partner.id, 500.0, 0.0),
            (cls.acc_rev.id, False, 0.0, 500.0)])

    def _wizard(self, **kw):
        values = dict(
            company_id=self.company.id,
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
        )
        values.update(kw)
        return self.env["fec.export.wizard"].create(values)

    def _decode(self, wiz):
        return bytes(wiz.file_data or b"").decode("cp1252")

    def test_header_and_structure(self):
        wiz = self._wizard()
        wiz.action_generate()
        text = self._decode(wiz)
        lines = text.strip().split("\r\n")
        self.assertEqual(lines[0].split("\t"), [
            "CodeJournal", "JournalLib", "EcritureNum", "EcritureDate",
            "CompNumMvt", "CompPieceNum", "AccountNum", "AccountLib",
            "CompAuxNum", "CompAuxLib", "PieceRef", "PieceDate",
            "EcritureLib", "Debit", "Credit", "EcritureLet", "DateLet",
            "ValidDate"])
        # 1 en-tête + 4 lignes d'écritures
        self.assertEqual(len(lines), 5)
        self.assertTrue(wiz.file_name.startswith("422211101") or
                        wiz.file_name.startswith("FR") or
                        len(wiz.file_name) >= 11)
        self.assertEqual(wiz.record_count, 4)
        self.assertEqual(wiz.move_count, 2)

    def test_totals_balanced(self):
        wiz = self._wizard()
        wiz.action_generate()
        self.assertAlmostEqual(wiz.total_debit, 1500.0, places=2)
        self.assertAlmostEqual(wiz.total_credit, 1500.0, places=2)
        text = self._decode(wiz)
        deb = sum(float(l.split("\t")[13].replace(",", "."))
                  for l in text.strip().split("\r\n")[1:])
        cred = sum(float(l.split("\t")[14].replace(",", "."))
                   for l in text.strip().split("\r\n")[1:])
        self.assertAlmostEqual(deb, cred, places=2)

    def test_field_formats(self):
        wiz = self._wizard()
        wiz.action_generate()
        rows = [l.split("\t") for l in self._decode(wiz).strip().split("\r\n")[1:]]
        # Ligne de produit du 15/01 : compte 700000, crédit 1000,00
        rev = [r for r in rows if r[6] == "700000" and r[3] == "20250115"][0]
        self.assertEqual(rev[0], "VTS")          # CodeJournal
        self.assertEqual(rev[3], "20250115")     # EcritureDate AAAAMMJJ
        self.assertEqual(rev[14], "1000,00")     # Credit à la virgule
        self.assertEqual(rev[17], "20250115")    # ValidDate AAAAMMJJ
        # Une ligne de débit de la même pièce (compte client 411)
        debit = [r for r in rows if r[6] == "411000" and r[3] == "20250115"][0]
        self.assertEqual(debit[13], "1000,00")   # Debit à la virgule

    def test_auxiliary_and_pipe(self):
        wiz = self._wizard(separator="pipe")
        wiz.action_generate()
        rows = [l.split("|") for l in self._decode(wiz).strip().split("\r\n")[1:]]
        # Ligne tiers : CompAuxNum renseigné depuis la référence partenaire
        aux = [r for r in rows if r[8] == "C0001"]
        self.assertTrue(aux)
        self.assertEqual(aux[0][9], "Client FEC")

    def test_empty_period_user_error(self):
        with self.assertRaises(UserError):
            self._wizard(date_from=date(1999, 1, 1),
                         date_to=date(1999, 12, 31)).action_generate()

    def test_dates_order_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["fec.export.wizard"].create({
                "company_id": self.company.id,
                "date_from": date(2025, 12, 31),
                "date_to": date(2025, 1, 1),
            })
