# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCustomerFeedback(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Feedback Customer"})
        cls.topic = cls.env["customer.feedback.topic"].create({"name": "Delivery"})
        cls.manager = cls._user(
            "feedback-manager", ["fs_customer_feedback.group_fscustomerfe_user"])
        cls.outsider = cls._user(
            "feedback-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _feedback(self, score="4"):
        return self.env["customer.feedback"].create({
            "partner_id": self.partner.id,
            "topic_id": self.topic.id,
            "score": score,
            "comment": "Test",
            "company_id": self.env.company.id,
        })

    def test_01_create_and_workflow(self):
        fb = self._feedback("2")
        self.assertEqual(fb.state, "new")
        fb.action_progress()
        self.assertEqual(fb.state, "progress")
        fb.action_done()
        self.assertEqual(fb.state, "done")
        fb.action_reset()
        self.assertEqual(fb.state, "new")

    def test_02_optional_order_link(self):
        product = self.env["product.product"].create({
            "name": "FB Product", "type": "service", "list_price": 10.0})
        order = self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "order_line": [(0, 0, {
                "product_id": product.id,
                "product_uom_qty": 1.0,
                "price_unit": 10.0,
            })],
        })
        fb = self.env["customer.feedback"].create({
            "partner_id": self.partner.id,
            "score": "5",
            "order_id": order.id,
            "company_id": self.env.company.id,
        })
        self.assertEqual(fb.order_id, order)

    def test_03_access_control(self):
        fb = self._feedback()
        with self.assertRaises(Exception):
            self.env["customer.feedback"].with_user(self.outsider).create({
                "partner_id": self.partner.id,
                "score": "3",
                "company_id": self.env.company.id,
            })
        fb.with_user(self.manager).read()

    def test_04_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "FB B"})
        partner_b = self.env["res.partner"].create({
            "name": "Cust B", "company_id": company_b.id})
        foreign = self.env["customer.feedback"].create({
            "partner_id": partner_b.id,
            "score": "3",
            "company_id": company_b.id,
        })
        visible = self.env["customer.feedback"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)

    def test_05_topic_and_reference(self):
        fb = self._feedback("5")
        self.assertEqual(fb.topic_id, self.topic)
        self.assertTrue(fb.name)
        self.assertEqual(fb.score, "5")
