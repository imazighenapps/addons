# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIntercoFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "InterCo Customer", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "InterCo Sold Product", "type": "consu",
            "list_price": 100.0, "standard_price": 60.0})
        cls.target_product = cls.env["product.product"].create({
            "name": "InterCo Bought Product", "type": "consu",
            "list_price": 120.0, "standard_price": 70.0})
        cls.buying_company = cls.env["res.company"].create({
            "name": "InterCo Buying Company"})

    def _order(self, qty=2.0, price=100.0):
        order = self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "order_line": [(0, 0, {
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "price_unit": price,
            })],
        })
        order.action_confirm()
        return order

    def _rule(self, **kwargs):
        values = {
            "name": "InterCo Rule",
            "target_company_id": self.buying_company.id,
            "price_mode": "margin",
            "margin_percent": 10.0,
        }
        values.update(kwargs)
        return self.env["interco.rule"].create(values)

    def _transfer(self, order=None, rule=None, **kwargs):
        order = order or self._order()
        rule = rule or self._rule(**kwargs)
        order.action_create_interco_transfer()
        return self.env["interco.transfer"].search(
            [("sale_order_id", "=", order.id)], limit=1)

    def test_01_transfer_is_built_from_the_order(self):
        transfer = self._transfer()
        self.assertEqual(len(transfer.line_ids), 1)
        line = transfer.line_ids
        self.assertEqual(line.source_product_id, self.product)
        self.assertAlmostEqual(line.product_qty, 2.0, places=2)
        self.assertAlmostEqual(transfer.amount_sale, 200.0, places=2)
        self.assertEqual(transfer.state, "draft")

    def test_02_margin_price_is_applied(self):
        transfer = self._transfer(margin_percent=25.0)
        line = transfer.line_ids
        self.assertAlmostEqual(line.price_unit, 125.0, places=2)
        self.assertAlmostEqual(line.subtotal, 250.0, places=2)
        self.assertAlmostEqual(transfer.amount_purchase, 250.0, places=2)
        self.assertAlmostEqual(transfer.margin_amount, -50.0, places=2)

    def test_03_cost_price_is_applied(self):
        transfer = self._transfer(price_mode="cost")
        self.assertAlmostEqual(transfer.line_ids.price_unit, 60.0, places=2)

    def test_04_same_price_is_applied(self):
        transfer = self._transfer(price_mode="same")
        self.assertAlmostEqual(transfer.line_ids.price_unit, 100.0, places=2)

    def test_05_mapping_overrides_product_and_price(self):
        rule = self._rule(margin_percent=10.0)
        self.env["interco.mapping"].create({
            "rule_id": rule.id,
            "source_product_id": self.product.id,
            "target_product_id": self.target_product.id,
            "price_unit": 90.0,
        })
        order = self._order()
        order.action_create_interco_transfer()
        transfer = self.env["interco.transfer"].search(
            [("sale_order_id", "=", order.id)], limit=1)
        line = transfer.line_ids
        self.assertEqual(line.target_product_id, self.target_product)
        self.assertAlmostEqual(line.price_unit, 90.0, places=2)

    def test_06_purchase_order_is_created_in_the_buying_company(self):
        transfer = self._transfer()
        action = transfer.action_create_purchase()
        self.assertEqual(action["res_model"], "purchase.order")
        order = transfer.purchase_order_id
        self.assertTrue(order)
        self.assertEqual(order.company_id, self.buying_company)
        self.assertEqual(order.partner_id, self.env.company.partner_id)
        self.assertEqual(order.origin, transfer.sale_order_id.name)
        self.assertEqual(len(order.order_line), 1)
        self.assertAlmostEqual(order.order_line.product_qty, 2.0, places=2)
        self.assertAlmostEqual(order.order_line.price_unit, 110.0, places=2)
        transfer.invalidate_recordset()
        self.assertEqual(transfer.state, "created")

    def test_07_a_second_transfer_is_refused(self):
        order = self._order()
        self._rule()
        order.action_create_interco_transfer()
        with self.assertRaises(Exception):
            self.env["interco.transfer"].create({
                "rule_id": self.env["interco.rule"].search([], limit=1).id,
                "sale_order_id": order.id,
                "target_company_id": self.buying_company.id,
            })
            self.env.flush_all()

    def test_08_rule_guards_and_cancel(self):
        rule = self._rule()
        with self.assertRaises(ValidationError):
            rule.target_company_id = self.env.company
        transfer = self._transfer(rule=rule)
        self.assertTrue(transfer.action_cancel())
        self.assertEqual(transfer.state, "cancelled")
        other = self.env["interco.rule"].create({
            "name": "InterCo Other Rule",
            "company_id": self.buying_company.id,
            "target_company_id": self.env.company.id,
        })
        self.assertNotEqual(other.company_id, transfer.company_id)
        order = self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "company_id": self.buying_company.id,
            "order_line": [(0, 0, {
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "price_unit": 100.0,
            })],
        })
        with self.assertRaises(UserError):
            rule._create_transfer(order)
