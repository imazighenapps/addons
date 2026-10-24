# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSubsFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Subscription Customer", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "Monthly Support", "type": "service",
            "list_price": 300.0, "taxes_id": [(5, 0, 0)]})
        cls.plan = cls.env["subs.plan"].create({
            "name": "Support Gold", "product_id": cls.product.id,
            "amount": 300.0, "interval": "monthly"})

    def _subscription(self, interval="monthly", amount=300.0,
                      date_start=None):
        return self.env["subs.subscription"].create({
            "partner_id": self.partner.id,
            "plan_id": self.plan.id,
            "amount": amount,
            "interval": interval,
            "date_start": date_start or date(2026, 1, 1),
        })

    def test_01_sequence(self):
        subscription = self._subscription()
        self.assertTrue(subscription.name.startswith("SUB/"))

    def test_02_mrr(self):
        subscription = self._subscription(interval="yearly", amount=1200.0)
        self.assertAlmostEqual(subscription.mrr, 100.0, places=2)
        self.assertAlmostEqual(subscription.arr, 1200.0, places=2)

    def test_03_start(self):
        subscription = self._subscription()
        subscription.action_start()
        self.assertEqual(subscription.state, "running")
        self.assertEqual(subscription.date_next_invoice, date(2026, 1, 1))

    def test_04_invoice_now(self):
        subscription = self._subscription()
        subscription.action_start()
        subscription.action_invoice_now()
        self.assertEqual(subscription.invoice_count, 1)
        invoice = subscription.invoice_ids
        self.assertEqual(invoice.move_type, "out_invoice")
        self.assertAlmostEqual(invoice.amount_total, 300.0, places=2)
        self.assertEqual(subscription.date_next_invoice, date(2026, 2, 1))

    def test_05_pause_and_resume(self):
        subscription = self._subscription()
        subscription.action_start()
        subscription.action_pause()
        self.assertEqual(subscription.state, "paused")
        subscription.action_resume()
        self.assertEqual(subscription.state, "running")

    def test_06_cron(self):
        subscription = self._subscription(date_start=date(2026, 1, 1))
        subscription.action_start()
        subscription.date_next_invoice = date(2026, 1, 1)
        self.env["subs.subscription"]._cron_invoice()
        self.assertEqual(subscription.invoice_count, 1)
        self.assertEqual(subscription.date_next_invoice, date(2026, 2, 1))

    def test_07_cron_ignores_paused(self):
        subscription = self._subscription()
        subscription.action_start()
        subscription.action_pause()
        subscription.date_next_invoice = date(2026, 1, 1)
        self.env["subs.subscription"]._cron_invoice()
        self.assertEqual(subscription.invoice_count, 0)

    def test_08_onchange_plan(self):
        subscription = self.env["subs.subscription"].new({
            "partner_id": self.partner.id,
            "plan_id": self.plan.id,
        })
        subscription._onchange_plan()
        self.assertAlmostEqual(subscription.amount, 300.0, places=2)
        self.assertEqual(subscription.interval, "monthly")
