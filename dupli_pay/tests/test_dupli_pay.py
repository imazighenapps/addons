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

    def _bill(self, amount, bill_date):
        bill = self.env["account.move"].create({
            "move_type": "in_invoice",
            "partner_id": self.partner.id,
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

    def _alerts(self):
        """Only the alerts raised for the partner used by these tests.

        The database may already contain demo bills, so a global search
        would be polluted by pre-existing duplicates.
        """
        return self.env["dupli.alert"].search(
            [("partner_id", "=", self.partner.id)])

    def test_01_scan_detects_duplicate(self):
        self._bill(100.0, date(2026, 1, 5))
        self._bill(100.0, date(2026, 1, 7))
        created = self.env["dupli.scanner"].action_scan()
        self.assertGreaterEqual(created, 1)
        alerts = self._alerts()
        self.assertTrue(alerts)
        self.assertAlmostEqual(alerts[0].amount, 100.0, places=2)

    def test_02_no_duplicate_when_amount_differs(self):
        self._bill(100.0, date(2026, 2, 5))
        self._bill(140.0, date(2026, 2, 6))
        self.env["dupli.scanner"].action_scan()
        self.assertFalse(self._alerts())

    def test_03_no_duplicate_when_dates_too_far(self):
        self._bill(100.0, date(2026, 3, 1))
        self._bill(100.0, date(2026, 4, 1))
        self.env["dupli.scanner"].action_scan()
        self.assertFalse(self._alerts())

    def test_04_alert_not_duplicated(self):
        self._bill(100.0, date(2026, 5, 5))
        self._bill(100.0, date(2026, 5, 6))
        self.env["dupli.scanner"].action_scan()
        count = len(self._alerts())
        self.env["dupli.scanner"].action_scan()
        self.assertEqual(len(self._alerts()), count)

    def test_05_workflow(self):
        self._bill(100.0, date(2026, 6, 5))
        self._bill(100.0, date(2026, 6, 6))
        self.env["dupli.scanner"].action_scan()
        alert = self._alerts()[:1]
        alert.action_ignore()
        self.assertEqual(alert.state, "ignored")
        alert.action_reset()
        self.assertEqual(alert.state, "open")
        alert.action_confirm()
        self.assertEqual(alert.state, "duplicate")
