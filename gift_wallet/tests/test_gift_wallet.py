# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGiftWallet(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Gift Customer"})

    def _card(self, amount=100.0, expiry=None):
        return self.env["gift.card"].create({
            "partner_id": self.partner.id,
            "initial_amount": amount,
            "expiry_date": expiry,
        })

    def test_01_code_and_issue(self):
        card = self._card()
        self.assertTrue(card.name.startswith("GC-"))
        self.assertEqual(card.state, "active")
        self.assertAlmostEqual(card.balance, 100.0, places=2)
        self.assertEqual(card.transaction_count, 1)
        self.assertEqual(card.transaction_ids.type, "issue")

    def test_02_partial_redemption(self):
        card = self._card()
        card.redeem(30.0, "Order S0001")
        self.assertAlmostEqual(card.balance, 70.0, places=2)
        self.assertEqual(card.state, "active")
        self.assertEqual(card.transaction_count, 2)

    def test_03_full_redemption(self):
        card = self._card()
        card.redeem(100.0)
        self.assertAlmostEqual(card.balance, 0.0, places=2)
        self.assertEqual(card.state, "used")
        with self.assertRaises(Exception):
            card.redeem(1.0)

    def test_04_reload(self):
        card = self._card(50.0)
        card.reload(25.0)
        self.assertAlmostEqual(card.balance, 75.0, places=2)
        self.assertEqual(card.transaction_ids.filtered(
            lambda t: t.type == "reload").amount, 25.0)

    def test_05_expired(self):
        card = self._card(50.0, expiry=date.today() - timedelta(days=1))
        with self.assertRaises(Exception):
            card.redeem(10.0)

    def test_06_cron_expire(self):
        card = self._card(50.0, expiry=date.today() - timedelta(days=1))
        self.env["gift.card"]._cron_expire()
        self.assertEqual(card.state, "expired")

    def test_07_wizard(self):
        card = self._card(80.0)
        wizard = self.env["gift.redeem.wizard"].create({
            "card_id": card.id, "amount": 20.0, "reference": "POS"})
        wizard.action_redeem()
        self.assertAlmostEqual(card.balance, 60.0, places=2)
