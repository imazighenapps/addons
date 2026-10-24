# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCommissionDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rep = cls.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Commission Test Rep",
            "login": "commission_test_rep",
            "group_ids": [(6, 0, [
                cls.env.ref("base.group_user").id,
                cls.env.ref("sales_team.group_sale_salesman").id,
            ])],
        })
        cls.partner = cls.env["res.partner"].create({
            "name": "Acme Distribution",
            "is_company": True,
        })
        cls.product = cls.env["product.product"].create({
            "name": "Industrial Kit",
            "type": "service",
            "list_price": 100.0,
            "standard_price": 60.0,
        })

    def _order(self, qty=10, price=100.0):
        order = self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "user_id": self.rep.id,
            "order_line": [(0, 0, {
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "price_unit": price,
            })],
        })
        order.action_confirm()
        return order

    def _statement(self):
        return self.env["commission.statement"].create({
            "user_id": self.rep.id,
            "date_from": date.today(),
            "date_to": date.today(),
        })

    def test_01_rule_specificity(self):
        generic = self.env["commission.rule"].create({
            "name": "Generic 5%", "basis": "order",
            "rate_type": "percent", "rate": 5.0,
        })
        specific = self.env["commission.rule"].create({
            "name": "Acme 10%", "basis": "order", "partner_id": self.partner.id,
            "rate_type": "percent", "rate": 10.0,
        })
        rule = self._statement()._find_rule(
            self.rep, False, self.partner, self.product.categ_id, date.today())
        self.assertEqual(rule, specific)
        self.assertNotEqual(rule, generic)

    def test_02_volume_tiers(self):
        rule = self.env["commission.rule"].create({
            "name": "Tiered", "basis": "order", "rate_type": "percent", "rate": 5.0,
            "tier_ids": [
                (0, 0, {"min_amount": 0.0, "max_amount": 1000.0, "rate": 5.0}),
                (0, 0, {"min_amount": 1000.0, "max_amount": 0.0, "rate": 8.0}),
            ],
        })
        statement = self._statement()
        self.assertEqual(statement._rate_for(rule, 1500.0), 8.0)
        rate, amount = statement._amount_for(rule, 1500.0)
        self.assertEqual(rate, 8.0)
        self.assertAlmostEqual(amount, 120.0, places=2)

    def test_03_generate_from_confirmed_order(self):
        self.env["commission.rule"].create({
            "name": "10% Orders", "basis": "order",
            "rate_type": "percent", "rate": 10.0,
        })
        order = self._order(qty=10, price=100.0)
        statement = self._statement()
        statement.action_generate_lines()
        self.assertEqual(len(statement.line_ids), 1)
        line = statement.line_ids
        self.assertEqual(line.sale_order_id, order)
        self.assertAlmostEqual(line.base_amount, 1000.0, places=2)
        self.assertAlmostEqual(line.amount, 100.0, places=2)
        self.assertAlmostEqual(statement.total_amount, 100.0, places=2)

    def test_04_fixed_amount(self):
        self.env["commission.rule"].create({
            "name": "Fixed 50", "basis": "order",
            "rate_type": "fixed", "rate": 50.0,
        })
        self._order(qty=10, price=100.0)
        statement = self._statement()
        statement.action_generate_lines()
        self.assertAlmostEqual(statement.line_ids.amount, 50.0, places=2)

    def test_05_workflow(self):
        self.env["commission.rule"].create({
            "name": "10% Orders", "basis": "order",
            "rate_type": "percent", "rate": 10.0,
        })
        self._order()
        statement = self._statement()
        statement.action_generate_lines()
        self.assertEqual(statement.state, "draft")
        statement.action_submit()
        self.assertEqual(statement.state, "submitted")
        statement.action_approve()
        self.assertEqual(statement.state, "approved")
        self.assertTrue(statement.approved_by)
        statement.action_pay()
        self.assertEqual(statement.state, "paid")
        self.assertEqual(statement.line_ids.state, "paid")

    def test_06_sale_order_smart_button(self):
        self.env["commission.rule"].create({
            "name": "10% Orders", "basis": "order",
            "rate_type": "percent", "rate": 10.0,
        })
        order = self._order()
        statement = self._statement()
        statement.action_generate_lines()
        order.invalidate_recordset()
        self.assertAlmostEqual(order.commission_total, 100.0, places=2)
        action = order.action_view_commissions()
        self.assertEqual(action["res_model"], "commission.line")

    def test_07_margin_basis(self):
        self.env["commission.rule"].create({
            "name": "Margin 20%", "basis": "order",
            "rate_type": "percent", "rate": 20.0, "use_margin": True,
        })
        self._order(qty=10, price=100.0)  # margin = (100 - 60) * 10 = 400
        statement = self._statement()
        statement.action_generate_lines()
        self.assertAlmostEqual(statement.line_ids.base_amount, 400.0, places=2)
        self.assertAlmostEqual(statement.line_ids.amount, 80.0, places=2)
