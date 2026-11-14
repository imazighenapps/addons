# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged
from odoo import fields


@tagged("post_install", "-at_install")
class TestSalePlanPay(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "SalePlan Test Customer"})
        cls.product = cls.env["product.product"].create({
            "name": "SalePlan Test Product",
            "type": "service",
            "list_price": 100.0,
        })
        cls.order = cls.env["sale.order"].create({
            "partner_id": cls.partner.id,
            "order_line": [(0, 0, {
                "product_id": cls.product.id,
                "product_uom_qty": 1.0,
                "price_unit": 300.0,
            })],
        })
        cls.order.action_confirm()

        cls.manager = cls._user(
            "saleplan-manager", ["sale_plan_pay.group_saleplanpay_user"])
        cls.outsider = cls._user(
            "saleplan-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields \
            else "groups_id"
        return cls.env["res.users"].create({
            "name": login,
            "login": login,
            field: [(6, 0, groups)],
        })

    def _make_plan(self):
        today = fields.Date.context_today(self.env.user)
        return self.env["sale.plan.pay"].create({
            "order_id": self.order.id,
            "partner_id": self.partner.id,
            "amount_total": self.order.amount_total,
            "currency_id": self.order.currency_id.id,
            "line_ids": [
                (0, 0, {"name": "Inst 1", "date_due": today,
                        "amount": self.order.amount_total / 3.0}),
                (0, 0, {"name": "Inst 2", "date_due": today,
                        "amount": self.order.amount_total / 3.0}),
                (0, 0, {"name": "Inst 3", "date_due": today,
                        "amount": self.order.amount_total
                        - 2.0 * (self.order.amount_total / 3.0)}),
            ],
        })

    def test_01_sum_must_match(self):
        plan = self._make_plan()
        plan.line_ids[0].amount = 10.0
        with self.assertRaises(UserError):
            plan.action_activate()

    def test_02_generate_invoice_once(self):
        plan = self._make_plan()
        plan.action_activate()
        self.assertEqual(plan.state, "active")
        line = plan.line_ids[0]
        action = line.action_create_invoice()
        self.assertTrue(line.move_id)
        self.assertEqual(action["res_id"], line.move_id.id)
        action2 = line.action_create_invoice()
        self.assertEqual(action2["res_id"], line.move_id.id)

    def test_03_status_planned_and_late(self):
        ref = fields.Date.context_today(self.env.user)
        past = fields.Date.subtract(ref, days=10)
        future = fields.Date.add(ref, days=10)
        plan = self.env["sale.plan.pay"].create({
            "order_id": self.order.id,
            "partner_id": self.partner.id,
            "amount_total": self.order.amount_total,
            "currency_id": self.order.currency_id.id,
            "line_ids": [
                (0, 0, {"name": "Past", "date_due": past,
                        "amount": self.order.amount_total / 2.0}),
                (0, 0, {"name": "Future", "date_due": future,
                        "amount": self.order.amount_total / 2.0}),
            ],
        })
        statuses = set(plan.line_ids.mapped("status"))
        self.assertIn("late", statuses)
        self.assertIn("planned", statuses)
        self.assertGreaterEqual(plan.late_count, 1)

    def test_04_access_control(self):
        plan = self._make_plan()
        with self.assertRaises(Exception):
            self.env["sale.plan.pay"].with_user(self.outsider).create({
                "order_id": self.order.id,
                "partner_id": self.partner.id,
                "amount_total": self.order.amount_total,
                "currency_id": self.order.currency_id.id,
            })
        plan.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "SalePlan B"})
        foreign = self.env["sale.plan.pay"].create({
            "order_id": self.order.id,
            "partner_id": self.partner.id,
            "amount_total": self.order.amount_total,
            "currency_id": self.order.currency_id.id,
            "company_id": company_b.id,
        })
        visible = self.env["sale.plan.pay"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
