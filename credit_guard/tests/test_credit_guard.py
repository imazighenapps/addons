# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCreditGuard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Credit Test Customer", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "Credit Test Product", "type": "service",
            "list_price": 100.0})
        cls.profile = cls.env["credit.profile"].create({
            "partner_id": cls.partner.id, "credit_limit": 1000.0,
            "block_mode": "block"})

    def _order(self, qty):
        return self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "order_line": [(0, 0, {
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "price_unit": 100.0,
            })],
        })

    def test_01_profile_unique(self):
        with self.assertRaises(Exception):
            self.env["credit.profile"].create({
                "partner_id": self.partner.id, "credit_limit": 50.0})

    def test_02_available_credit(self):
        self.profile.invalidate_recordset()
        self.assertAlmostEqual(self.profile.available, 1000.0, places=2)

    def test_03_block_over_limit(self):
        order = self._order(15)
        with self.assertRaises(UserError):
            order.action_confirm()

    def test_04_within_limit(self):
        order = self._order(5)
        order.action_confirm()
        self.assertEqual(order.state, "sale")

    def test_05_warn_mode_allows(self):
        self.profile.block_mode = "warn"
        order = self._order(15)
        order.action_confirm()
        self.assertEqual(order.state, "sale")

    def test_06_override_allows(self):
        order = self._order(15)
        override = self.env["credit.override"].create({
            "partner_id": self.partner.id,
            "sale_order_id": order.id,
            "amount": order.amount_total,
            "reason": "Strategic customer",
        })
        override.action_approve()
        order.credit_override_id = override.id
        order.action_confirm()
        self.assertEqual(order.state, "sale")

    def test_07_blocked_profile(self):
        self.profile.action_block()
        order = self._order(1)
        self.assertEqual(order.credit_state, "blocked")

    def test_08_override_workflow(self):
        override = self.env["credit.override"].create({
            "partner_id": self.partner.id, "reason": "Test"})
        self.assertTrue(override.name.startswith("CRO/"))
        override.action_approve()
        self.assertEqual(override.state, "approved")
        self.assertTrue(override.approved_by)
        with self.assertRaises(UserError):
            override.action_approve()

    def test_09_exposure_from_confirmed_order(self):
        order = self._order(5)
        order.action_confirm()
        total = order.amount_total
        self.profile.invalidate_recordset()
        self.assertAlmostEqual(self.profile.exposure, total, places=2)
        self.assertAlmostEqual(self.profile.available, 1000.0 - total, places=2)
        self.assertAlmostEqual(self.profile.usage, total / 10.0, places=1)
