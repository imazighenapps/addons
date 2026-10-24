# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBackInStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1)
        cls.product = cls.env["product.product"].create({
            "name": "Waiting Product", "type": "consu", "is_storable": True,
            "list_price": 49.0})

    def _request(self, email="waiting@example.com"):
        return self.env["stock.alert.request"].create({
            "product_id": self.product.id, "email": email})

    def test_01_create(self):
        request = self._request()
        self.assertEqual(request.state, "pending")
        self.assertIn("Waiting Product", request.name)
        self.assertTrue(request.consent_date)

    def test_02_bad_email(self):
        with self.assertRaises(Exception):
            self._request("not-an-email")

    def test_03_no_stock_no_alert(self):
        request = self._request()
        self.env["stock.alert.request"]._cron_notify()
        self.assertEqual(request.state, "pending")

    def test_04_alert_when_stock_available(self):
        request = self._request()
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.warehouse.lot_stock_id, 5.0)
        self.product.invalidate_recordset()
        self.env["stock.alert.request"]._cron_notify()
        self.assertEqual(request.state, "notified")
        self.assertTrue(request.notified_date)

    def test_05_notify_action(self):
        request = self._request()
        request.action_notify()
        self.assertEqual(request.state, "notified")
        request.action_reset()
        self.assertEqual(request.state, "pending")

    def test_06_subscribe_deduplicates(self):
        first = self.env["stock.alert.request"].subscribe(
            self.product.id, "Client@Example.com")
        second = self.env["stock.alert.request"].subscribe(
            self.product.id, "client@example.com")
        self.assertEqual(first, second)
        self.assertEqual(first.source, "api")

    def test_07_product_count(self):
        self._request()
        self.product.product_tmpl_id.invalidate_recordset()
        self.assertEqual(self.product.product_tmpl_id.alert_request_count, 1)
