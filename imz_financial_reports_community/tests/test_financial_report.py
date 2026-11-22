# -*- coding: utf-8 -*-
from datetime import date

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFinancialReports(TransactionCase):
    """Tests fonctionnels réels du moteur d'états financiers."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context={"check_move_validity": True})
        cls.company = cls.env.company
        # Comptes de test (internal_group est calculé depuis account_type)
        cls.acc_rev = cls.env["account.account"].create({
            "name": "Ventes test", "code": "700100",
            "account_type": "income",
        })
        cls.acc_exp = cls.env["account.account"].create({
            "name": "Achats test", "code": "601100",
            "account_type": "expense",
        })
        cls.acc_cash = cls.env["account.account"].create({
            "name": "Caisse test", "code": "580100",
            "account_type": "asset_cash",
        })
        cls.journal = cls.env["account.journal"].create({
            "name": "Journal général test", "code": "TGT", "type": "general",
            "company_id": cls.company.id,
        })

        def move(dates, lines):
            m = cls.env["account.move"].create({
                "journal_id": cls.journal.id,
                "date": dates,
                "move_type": "entry",
                "line_ids": [Command.create({
                    "account_id": acc, "debit": deb, "credit": cred,
                }) for (acc, deb, cred) in lines],
            })
            m.action_post()
            return m

        # Exercice 2025 : 1000 de ventes, 400 de charges (écritures équilibrées)
        move(date(2025, 1, 15), [(cls.acc_cash.id, 1000.0, 0.0),
                                 (cls.acc_rev.id, 0.0, 1000.0),
                                 (cls.acc_exp.id, 400.0, 0.0),
                                 (cls.acc_cash.id, 0.0, 400.0)])
        # Exercice 2024 (comparaison) : 800 de ventes, 500 de charges
        move(date(2024, 7, 10), [(cls.acc_cash.id, 800.0, 0.0),
                                 (cls.acc_rev.id, 0.0, 800.0),
                                 (cls.acc_exp.id, 500.0, 0.0),
                                 (cls.acc_cash.id, 0.0, 500.0)])

    def _make_report(self):
        report = self.env["fr.report"].create({
            "name": "Compte de résultat test",
            "report_type": "pl",
            "line_ids": [
                Command.create({
                    "line_type": "title", "name": "Produits",
                }),
                Command.create({
                    "line_type": "line", "name": "Ventes", "code": "PROD",
                    "sign": "-1", "code_prefixes": "7", "parent_id": None,
                }),
                Command.create({
                    "line_type": "line", "name": "Charges", "code": "CHG",
                    "sign": "-1", "code_prefixes": "6", "parent_id": None,
                }),
                Command.create({
                    "line_type": "subtotal", "name": "Résultat", "code": "RES",
                }),
            ],
        })
        # Résultat = Produits (sens -1 => credit-debit) + Charges (debit-credit)
        # Rattacher les lignes Produits/Charges au sous-total :
        lines = report.line_ids
        lines[1].parent_id = lines[3].id
        lines[2].parent_id = lines[3].id
        return report

    def test_line_aggregation(self):
        report = self._make_report()
        lines = report.line_ids
        sales = lines.filtered(lambda l: l.code == "PROD")
        wiz = self.env["fr.report.wizard"].create({
            "report_id": report.id,
            "date_from": date(2025, 1, 1),
            "date_to": date(2025, 12, 31),
            "detailed": False,
        })
        rows = {r["line"]["code"]: r["amount"] for r in wiz._compute_period(
            wiz.date_from, wiz.date_to) if r["line"]["code"]}
        # Ventes = crédit - débit (sens -1) => 1000
        self.assertAlmostEqual(rows["PROD"], 1000.0, 2, msg="Solde produits")
        # Charges en sens -1 (crédit - débit) => -400
        self.assertAlmostEqual(rows["CHG"], -400.0, 2, msg="Solde charges")
        # Résultat = 1000 - 400
        self.assertAlmostEqual(rows["RES"], 600.0, 2, msg="Résultat")

    def test_prefix_and_group_sources_agree(self):
        """La même ligne via préfixe ou via groupe interne doit donner le même solde."""
        line_pref = self.env["fr.report.line"].create({
            "report_id": self._make_report().id,
            "name": "Via préfixe", "code_prefixes": "7", "sign": "-1",
        })
        line_group = self.env["fr.report.line"].create({
            "report_id": line_pref.report_id.id,
            "name": "Via groupe", "internal_group": "income", "sign": "-1",
        })
        wiz = self.env["fr.report.wizard"].create({
            "report_id": line_pref.report_id.id,
            "date_from": date(2025, 1, 1),
            "date_to": date(2025, 12, 31),
            "detailed": False,
        })
        a, _ = wiz._aggregate_line(line_pref, wiz.date_from, wiz.date_to)
        b, _ = wiz._aggregate_line(line_group, wiz.date_from, wiz.date_to)
        self.assertAlmostEqual(a, b, 2)
        self.assertAlmostEqual(a, 1000.0, 2)

    def test_compare_periods(self):
        report = self._make_report()
        wiz = self.env["fr.report.wizard"].create({
            "report_id": report.id,
            "date_from": date(2025, 1, 1),
            "date_to": date(2025, 12, 31),
            "compare": True,
            "compare_from": date(2024, 1, 1),
            "compare_to": date(2024, 12, 31),
            "detailed": False,
        })
        data = wiz._execute()
        rows = {r["line"]["code"]: r["amount"] for r in data["rows"] if r["line"]["code"]}
        crows = {r["line"]["code"]: r["amount"]
                 for r in data["compare"]["rows"] if r["line"]["code"]}
        self.assertAlmostEqual(rows["PROD"] - crows["PROD"], 200.0, 2)

    def test_date_validation(self):
        report = self._make_report()
        with self.assertRaises(UserError):
            self.env["fr.report.wizard"].create({
                "report_id": report.id,
                "date_from": date(2025, 12, 31),
                "date_to": date(2025, 1, 1),
            })

    def test_line_constraints(self):
        report = self._make_report()
        with self.assertRaises(UserError):
            self.env["fr.report.line"].create({
                "report_id": report.id, "name": "Vide", "line_type": "line",
            })
        with self.assertRaises(UserError):
            self.env["fr.report.line"].create({
                "report_id": report.id, "name": "Deux sources",
                "line_type": "line", "code_prefixes": "7",
                "internal_group": "income",
            })
        with self.assertRaises(UserError):
            self.env["fr.report.line"].create({
                "report_id": report.id, "name": "Préfixe invalide",
                "code_prefixes": "7x,abc", "line_type": "line",
            })

    def test_csv_export(self):
        report = self._make_report()
        wiz = self.env["fr.report.wizard"].create({
            "report_id": report.id,
            "date_from": date(2025, 1, 1),
            "date_to": date(2025, 12, 31),
            "detailed": False,
        })
        res = wiz.action_export_csv()
        self.assertEqual(res["type"], "ir.actions.act_url")
        self.assertTrue(self.env["ir.attachment"].search_count(
            [("name", "like", "pl_2025-01-01_2025-12-31.csv")]))
