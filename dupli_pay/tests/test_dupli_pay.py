# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDupliPay(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Duplicate Supplier", "supplier_rank": 1})
        cls.product = cls.env["product.product"].create({
            "name": "Duplicate Product", "type": "service",
            "standard_price": 100.0, "list_price": 100.0})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1)
        cls.income = cls.env["account.account"].search(
            [("account_type", "=", "expense"),
             ("company_ids", "in", cls.env.company.id)], limit=1)

    def _partner(self, name):
        return self.env["res.partner"].create({
            "name": name, "supplier_rank": 1})

    def _bill(self, amount, bill_date, partner=None):
        partner = partner or self.partner
        bill = self.env["account.move"].create({
            "move_type": "in_invoice",
            "partner_id": partner.id,
            "journal_id": self.journal.id,
            "invoice_date": bill_date,
            "invoice_line_ids": [(0, 0, {
                "product_id": self.product.id,
                "name": "Service",
                "quantity": 1, "price_unit": amount,
                "tax_ids": [(5, 0, 0)]})],
        })
        bill.action_post()
        return bill

    def test_01_scan_detects_duplicate(self):
        partner = self._partner("Dupli Case 01")
        self._bill(100.0, date(2026, 1, 5), partner)
        self._bill(100.0, date(2026, 1, 7), partner)
        self.env["dupli.scanner"].action_scan()
        alerts = self.env["dupli.alert"].search([
            ("partner_id", "=", partner.id)])
        self.assertEqual(len(alerts), 1)
        self.assertAlmostEqual(alerts.amount, 100.0, places=2)

    def test_02_no_duplicate_when_amount_differs(self):
        partner = self._partner("Dupli Case 02")
        self._bill(100.0, date(2026, 2, 5), partner)
        self._bill(140.0, date(2026, 2, 6), partner)
        self.env["dupli.scanner"].action_scan()
        self.assertFalse(self.env["dupli.alert"].search([
            ("partner_id", "=", partner.id)]))

    def test_03_no_duplicate_when_dates_too_far(self):
        partner = self._partner("Dupli Case 03")
        self._bill(100.0, date(2026, 3, 1), partner)
        self._bill(100.0, date(2026, 4, 1), partner)
        self.env["dupli.scanner"].action_scan()
        self.assertFalse(self.env["dupli.alert"].search([
            ("partner_id", "=", partner.id)]))

    def test_04_alert_not_duplicated(self):
        partner = self._partner("Dupli Case 04")
        self._bill(100.0, date(2026, 5, 5), partner)
        self._bill(100.0, date(2026, 5, 6), partner)
        self.env["dupli.scanner"].action_scan()
        alerts = self.env["dupli.alert"].search([
            ("partner_id", "=", partner.id)])
        self.env["dupli.scanner"].action_scan()
        self.assertEqual(len(alerts), self.env["dupli.alert"].search_count([
            ("partner_id", "=", partner.id)]))

    def test_05_workflow(self):
        partner = self._partner("Dupli Case 05")
        self._bill(100.0, date(2026, 6, 5), partner)
        self._bill(100.0, date(2026, 6, 6), partner)
        self.env["dupli.scanner"].action_scan()
        alert = self.env["dupli.alert"].search([
            ("partner_id", "=", partner.id)], limit=1)
        alert.action_ignore()
        self.assertEqual(alert.state, "ignored")
        alert.action_reset()
        self.assertEqual(alert.state, "open")
        alert.action_confirm()
        self.assertEqual(alert.state, "duplicate")
