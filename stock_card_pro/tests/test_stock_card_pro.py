# -*- coding: utf-8 -*-
from datetime import date, datetime

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockCard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.customer = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create({
            "name": "Stock Card Test Product", "type": "consu",
            "is_storable": True, "standard_price": 12.0, "list_price": 25.0})
        cls.partner = cls.env["res.partner"].create({"name": "Stock Test Partner"})

    def _move(self, qty, source, dest):
        move = self.env["stock.move"].create({
            "name": "Test move",
            "product_id": self.product.id,
            "product_uom_qty": qty,
            "product_uom": self.product.uom_id.id,
            "location_id": source.id,
            "location_dest_id": dest.id,
        })
        move._action_confirm()
        move._action_assign()
        for line in move.move_line_ids:
            line.quantity = qty
        move.picked = True
        move._action_done()
        return move

    def _card(self):
        return self.env["stock.card"].create({
            "product_id": self.product.id,
            "location_id": self.stock.id,
            "date_from": date(2025, 1, 1),
            "date_to": date(2030, 12, 31),
            "unit_cost": 12.0,
        })

    def test_01_sequence(self):
        card = self._card()
        self.assertTrue(card.name.startswith("SC/"))

    def test_02_inbound(self):
        self._move(10.0, self.env.ref("stock.stock_location_suppliers"), self.stock)
        card = self._card()
        card.action_generate()
        self.assertAlmostEqual(card.in_qty, 10.0, places=2)
        self.assertAlmostEqual(card.closing_qty, 10.0, places=2)
        self.assertAlmostEqual(card.closing_value, 120.0, places=2)

    def test_03_outbound(self):
        self._move(10.0, self.env.ref("stock.stock_location_suppliers"), self.stock)
        self._move(4.0, self.stock, self.customer)
        card = self._card()
        card.action_generate()
        self.assertAlmostEqual(card.out_qty, 4.0, places=2)
        self.assertAlmostEqual(card.closing_qty, 6.0, places=2)

    def test_04_opening_quantity(self):
        move = self._move(7.0, self.env.ref("stock.stock_location_suppliers"), self.stock)
        move.date = datetime(2025, 6, 1, 10, 0, 0)
        card = self.env["stock.card"].create({
            "product_id": self.product.id,
            "location_id": self.stock.id,
            "date_from": date(2026, 1, 1),
            "date_to": date(2030, 12, 31),
            "unit_cost": 12.0,
        })
        card.action_generate()
        self.assertAlmostEqual(card.opening_qty, 7.0, places=2)
        self.assertAlmostEqual(card.closing_qty, 7.0, places=2)

    def test_05_empty_card(self):
        card = self.env["stock.card"].create({
            "product_id": self.product.id,
            "location_id": self.stock.id,
            "date_from": date(2026, 1, 1),
            "date_to": date(2026, 12, 31),
        })
        card.action_generate()
        self.assertEqual(card.closing_qty, 0.0)
        self.assertEqual(card.line_ids, self.env["stock.card.line"])
