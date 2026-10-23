# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


def _luhn_key(num_str):
    """Check digit making num_str + key Luhn-valid."""
    total = 0
    for i, ch in enumerate(reversed(num_str + "0")):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return str((10 - total % 10) % 10)


def _valid_siren(base8):
    """Find a Luhn-valid 9-digit SIREN starting with the 8-digit base."""
    from ..models.fr_tools import luhn_valid
    for i in range(10):
        candidate = "%s%d" % (base8[:8], i)
        if luhn_valid(candidate):
            return candidate
    return False


def _valid_siret(siren9):
    """Build a fully Luhn-valid 14-digit SIRET from a valid SIREN."""
    nic = siren9 + "0001"
    return nic + _luhn_key(nic)


def _fr_vat_for_siren(siren9):
    """Official French VAT key: key = (12 + 3 * (SIREN mod 97)) mod 97."""
    key = (12 + 3 * (int(siren9) % 97)) % 97
    return "FR%02d%s" % (key, siren9)


@tagged("post_install", "-at_install")
class TestFrEinvoicing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.country_id = cls.env.ref("base.fr")
        cls.company.account_fiscal_country_id = cls.env.ref("base.fr")
        cls.company_siren = _valid_siren("73282932")
        cls.company_siret = _valid_siret(cls.company_siren)
        cls.company.partner_id.write({
            "fr_siren": cls.company_siren,
            "fr_siret": cls.company_siret,
            "vat": _fr_vat_for_siren(cls.company_siren),
        })
        fr = cls.env.ref("base.fr")
        tax_group = cls.env["account.tax.group"].search(
            [("country_id", "=", fr.id)], limit=1
        )
        if not tax_group:
            tax_group = cls.env["account.tax.group"].create({
                "name": "TVA",
                "country_id": fr.id,
            })
        # search-or-create: a plain create() breaks on any database that
        # already carries a French VAT tax, and the test must be re-runnable.
        cls.tax = cls.env["account.tax"].search([
            ("name", "=", "TVA 20%"),
            ("type_tax_use", "=", "sale"),
            ("company_id", "=", cls.env.company.id),
        ], limit=1)
        if not cls.tax:
            cls.tax = cls.env["account.tax"].create({
                "name": "TVA 20%",
                "amount": 20.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "country_id": fr.id,
                "tax_group_id": tax_group.id,
            })
        cls.receivable = cls.env["account.account"].create({
            "name": "Test Receivable",
            "code": "411TEST",
            "account_type": "asset_receivable",
        })
        cls.income = cls.env["account.account"].create({
            "name": "Test Income",
            "code": "707TEST",
            "account_type": "income",
        })
        cls.partner_siren = _valid_siren("44306184")
        cls.partner_siret = _valid_siret(cls.partner_siren)
        cls.partner = cls.env["res.partner"].create({
            "name": "Client Test",
            "is_company": True,
            "country_id": fr.id,
            "fr_siren": cls.partner_siren,
            "fr_siret": cls.partner_siret,
            "vat": _fr_vat_for_siren(cls.partner_siren),
            "property_account_receivable_id": cls.receivable.id,
        })

    def _make_invoice(self):
        journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.company.id)], limit=1
        )
        return self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "journal_id": journal.id,
            "invoice_date": "2026-10-01",
            "fr_operation_type": "goods",
            "invoice_line_ids": [(0, 0, {
                "name": "Test product",
                "quantity": 2.0,
                "price_unit": 100.0,
                "tax_ids": [(6, 0, self.tax.ids)],
                "account_id": self.income.id,
            })],
        })

    def test_01_luhn_helpers(self):
        from ..models.fr_tools import is_siren, is_siret, siren_from_siret, is_fr_vat
        siren = _valid_siren("73282932")
        siret = _valid_siret(siren)
        self.assertTrue(is_siren(siren))
        self.assertTrue(is_siret(siret))
        self.assertEqual(siren_from_siret(siret), siren)
        self.assertFalse(is_siret("12345678901234"))
        self.assertFalse(is_siren("12345678"))
        self.assertTrue(is_fr_vat(_fr_vat_for_siren(siren)))
        self.assertFalse(is_fr_vat("FRXX123"))

    def test_02_partner_constraints(self):
        with self.assertRaises(ValidationError):
            self.partner.fr_siret = "12345678901234"

    def test_03_partner_readiness(self):
        self.assertTrue(self.partner.fr_einvoicing_ready)
        self.partner.fr_siren = False
        self.partner.fr_siret = False
        self.assertFalse(self.partner.fr_einvoicing_ready)
        self.assertIn("SIREN", self.partner.fr_einvoicing_issues)

    def test_04_post_blocked_then_allowed(self):
        move = self._make_invoice()
        move.fr_operation_type = False
        with self.assertRaises(UserError):
            move.action_post()
        move.fr_operation_type = "services"
        move.action_post()
        self.assertEqual(move.state, "posted")
        self.assertEqual(move.fr_validation_state, "ok")

    def test_05_facturx_xml(self):
        move = self._make_invoice()
        move.action_post()
        xml_bytes = move._fr_build_facturx()
        text = xml_bytes.decode("utf-8")
        self.assertIn("CrossIndustryInvoice", text)
        self.assertIn("urn:cen.eu:en16931:2017", text)
        self.assertIn("<ram:TypeCode>380</ram:TypeCode>", text)
        self.assertIn("240.00", text)  # 2 x 100 + 20% VAT = 240 total
        self.assertIn("200.00", text)  # untaxed

    def test_06_ereport_register(self):
        move = self._make_invoice()
        move.action_post()
        self.assertEqual(move.fr_ereport_status, "ready")
        lines = move.fr_ereport_line_ids
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines.flow, "einvoice_b2b")
        lines.action_mark_sent()
        self.assertEqual(lines.status, "sent")
