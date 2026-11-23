# -*- coding: utf-8 -*-
"""Tests fonctionnels de l'export SAF-T."""
import base64
from datetime import date

from lxml import etree

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged

NS = {"s": "urn:OECD:StandardAuditFile-Taxation:1.0"}


@tagged("post_install", "-at_install")
class TestSaftExport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        if not cls.company.vat:
            cls.company.vat = "FR32422111011"
        cls.profile = cls.env["saft.country.profile"].create({
            "name": "Portugal (test)", "country_id": cls.env.ref("base.pt").id,
            "namespace": "urn:OECD:StandardAuditFile-Taxation:1.0",
            "schema_version": "1.0",
        })
        cls.journal = cls.env["account.journal"].create({
            "name": "Journal SAF-T", "code": "SFT", "type": "general",
            "company_id": cls.company.id,
        })
        cls.acc_rev = cls.env["account.account"].create({
            "name": "Ventes SAF-T", "code": "701000",
            "account_type": "income"})
        cls.acc_cash = cls.env["account.account"].create({
            "name": "Caisse SAF-T", "code": "580001",
            "account_type": "asset_cash"})
        cls.tax = cls.env["account.tax"].create({
            "name": "TVA test 20%", "amount": 20.0,
            "amount_type": "percent", "type_tax_use": "sale"})
        cls.customer = cls.env["res.partner"].create({
            "name": "Client SAF-T", "ref": "CSAFT", "vat": "PT123456789",
            "customer_rank": 1,
        })

        move = cls.env["account.move"].create({
            "journal_id": cls.journal.id,
            "date": date(2025, 3, 15),
            "move_type": "entry",
            "ref": "SAFT-REF-1",
            "line_ids": [
                Command.create({"account_id": cls.acc_cash.id,
                                "partner_id": cls.customer.id,
                                "debit": 1200.0, "credit": 0.0}),
                Command.create({"account_id": cls.acc_rev.id,
                                "debit": 0.0, "credit": 1000.0}),
                Command.create({"account_id": cls.acc_rev.id,
                                "debit": 0.0, "credit": 200.0}),
            ],
        })
        move.action_post()

    def _export(self, **kw):
        values = dict(
            company_id=self.company.id,
            country_profile_id=self.profile.id,
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
        )
        values.update(kw)
        return self.env["saft.export"].create(values)

    def _xml(self, export):
        data = bytes(export.file_data or b"")
        if data[:1] not in (b"<",) and not data.startswith(b"\xef\xbb\xbf"):
            data = base64.b64decode(data)
        return etree.fromstring(data)

    def test_generation_and_structure(self):
        export = self._export(date_from=date(2025, 3, 1), date_to=date(2025, 3, 31))
        export.action_generate()
        self.assertEqual(export.state, "generated")
        self.assertTrue(export.file_name.startswith("SAFT_PT_"))
        root = self._xml(export)
        self.assertEqual(root.tag, "{urn:OECD:StandardAuditFile-Taxation:1.0}"
                                   "AuditFile")
        header = root.find("s:Header", NS)
        self.assertIsNotNone(header)
        self.assertEqual(header.findtext("s:AuditFileCountry", namespaces=NS),
                         "PT")
        company = header.find("s:Company", NS)
        self.assertEqual(
            company.findtext("s:TaxRegistrationNumber", namespaces=NS),
            "FR32422111011")
        entries = root.find("s:GeneralLedgerEntries", NS)
        self.assertEqual(entries.findtext("s:NumberEntries",
                                          namespaces=NS), "1")
        self.assertEqual(export.entry_count, 1)
        self.assertEqual(export.line_count, 3)
        self.assertAlmostEqual(export.total_debit, 1200.0, places=2)
        self.assertAlmostEqual(export.total_credit, 1200.0, places=2)

    def test_account_type_fallback_and_mapping(self):
        # Fallback internal_group : income -> SalesRevenue
        export = self._export()
        export.action_generate()
        root = self._xml(export)
        types = {a.findtext("s:AccountID", namespaces=NS):
                 a.findtext("s:AccountType", namespaces=NS)
                 for a in root.iter("{urn:OECD:StandardAuditFile-Taxation:1.0}"
                                    "Account")}
        self.assertEqual(types.get("701000"), "SalesRevenue")
        self.assertEqual(types.get("580001"), "CurrentAssets")

        # Mapping explicite écrase le fallback
        self.env["saft.account.map"].create({
            "profile_id": self.profile.id,
            "account_id": self.acc_cash.id,
            "saft_account_type": "Stock",
        })
        export2 = self._export()
        export2.action_generate()
        root2 = self._xml(export2)
        types2 = {a.findtext("s:AccountID", namespaces=NS):
                  a.findtext("s:AccountType", namespaces=NS)
                  for a in root2.iter("{urn:OECD:StandardAuditFile-Taxation:1.0}"
                                      "Account")}
        self.assertEqual(types2.get("580001"), "Stock")

    def test_completeness_warnings(self):
        export = self._export(date_from=date(2025, 3, 1), date_to=date(2025, 3, 31))
        export.action_check_completeness()
        self.assertIn("701000", export.warnings)

        # Mapping explicite exigé -> avertissement renforcé
        self.profile.require_explicit_account_map = True
        export.action_check_completeness()
        self.assertIn("mapping explicite", export.warnings)

        # Une fois tout mappé, plus d'avertissement
        self.env["saft.account.map"].create({
            "profile_id": self.profile.id,
            "account_id": self.acc_rev.id,
            "saft_account_type": "SalesRevenue"})
        self.env["saft.account.map"].create({
            "profile_id": self.profile.id,
            "account_id": self.acc_cash.id,
            "saft_account_type": "CurrentAssets"})
        export.action_check_completeness()
        self.assertIn("Complétude OK", export.warnings)

    def test_tax_table_entries(self):
        # Écriture utilisant la taxe pour qu'elle apparaisse dans la table
        move = self.env["account.move"].create({
            "journal_id": self.journal.id,
            "date": date(2025, 4, 1),
            "move_type": "entry",
            "line_ids": [
                Command.create({"account_id": self.acc_cash.id,
                                "debit": 100.0, "credit": 0.0}),
                Command.create({"account_id": self.acc_rev.id,
                                "debit": 0.0, "credit": 100.0,
                                "tax_ids": [Command.set([self.tax.id])]}),
            ],
        })
        move.action_post()
        self.env["saft.tax.map"].create({
            "profile_id": self.profile.id,
            "tax_id": self.tax.id,
            "saft_tax_code": "NOR", "saft_tax_rate": 20.0})
        export = self._export(date_from=date(2025, 4, 1), date_to=date(2025, 4, 30))
        export.action_generate()
        root = self._xml(export)
        table_entries = root.findall(
            "s:MasterFiles/s:TaxTable/s:TaxTableEntry", NS)
        self.assertGreaterEqual(len(table_entries), 1)
        codes = [e.findtext("s:TaxCode", namespaces=NS) for e in table_entries]
        self.assertIn("NOR", codes)

    def test_customer_master_file(self):
        export = self._export(date_from=date(2025, 3, 1), date_to=date(2025, 3, 31))
        export.action_generate()
        root = self._xml(export)
        customers = root.findall(
            "s:MasterFiles/s:Customers/s:Customer", NS)
        ids = [c.findtext("s:CustomerID", namespaces=NS) for c in customers]
        self.assertIn("CSAFT", ids)
        csaft = [c for c in customers if c.findtext("s:CustomerID", namespaces=NS) == "CSAFT"][0]
        self.assertEqual(
            csaft.findtext("s:CustomerTaxID", namespaces=NS),
            "PT123456789")

    def test_empty_period_user_error(self):
        export = self._export(date_from=date(1999, 1, 1),
                              date_to=date(1999, 12, 31))
        with self.assertRaises(UserError):
            export.action_generate()

    def test_date_order_constraint(self):
        with self.assertRaises(ValidationError):
            self._export(date_from=date(2025, 12, 31),
                         date_to=date(2025, 1, 1))

    def test_unique_account_mapping(self):
        self.env["saft.account.map"].search([
            ("profile_id", "=", self.profile.id),
            ("account_id", "=", self.acc_cash.id),
        ]).unlink()
        self.env["saft.account.map"].create({
            "profile_id": self.profile.id,
            "account_id": self.acc_cash.id,
            "saft_account_type": "Stock"})
        with self.assertRaises(Exception):
            with self.env.cr.savepoint():
                self.env["saft.account.map"].create({
                    "profile_id": self.profile.id,
                    "account_id": self.acc_cash.id,
                    "saft_account_type": "FixedAssets"})
