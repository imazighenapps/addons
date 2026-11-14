# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseRequisition(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Req Employee"})
        cls.product = cls.env["product.product"].create({
            "name": "Req Product",
            "type": "consu",
            "standard_price": 10.0,
        })
        cls.manager = cls._user(
            "purchasereq-manager", ["purchase_request.group_purchaserequ_user"])
        cls.outsider = cls._user(
            "purchasereq-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _req(self):
        return self.env["purchase.request"].create({
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
            "line_ids": [(0, 0, {
                "name": "Paper",
                "quantity": 5.0,
                "price_unit": 2.0,
            })],
        })

    def test_01_flow_submit_approve_order_done(self):
        req = self._req()
        self.assertAlmostEqual(req.amount_estimated, 10.0)
        req.action_submit()
        self.assertEqual(req.state, "submitted")
        req.action_approve()
        self.assertEqual(req.state, "approved")
        req.action_ordered()
        self.assertEqual(req.state, "ordered")
        req.action_done()
        self.assertEqual(req.state, "done")

    def test_02_submit_requires_lines(self):
        req = self.env["purchase.request"].create({
            "company_id": self.env.company.id,
        })
        with self.assertRaises(UserError):
            req.action_submit()

    def test_03_state_guards(self):
        req = self._req()
        with self.assertRaises(UserError):
            req.action_approve()
        req.action_submit()
        with self.assertRaises(UserError):
            req.action_ordered()

    def test_04_line_validation(self):
        with self.assertRaises(ValidationError):
            self.env["purchase.request"].create({
                "company_id": self.env.company.id,
                "line_ids": [(0, 0, {"name": "Bad", "quantity": 0.0, "price_unit": 1.0})],
            })

    def test_05_access_control(self):
        req = self._req()
        with self.assertRaises(Exception):
            self.env["purchase.request"].with_user(self.outsider).create({
                "company_id": self.env.company.id,
                "line_ids": [(0, 0, {"name": "X", "quantity": 1.0, "price_unit": 1.0})],
            })
        req.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Req B"})
        foreign = self.env["purchase.request"].create({
            "company_id": company_b.id,
            "line_ids": [(0, 0, {"name": "Foreign", "quantity": 1.0, "price_unit": 1.0})],
        })
        visible = self.env["purchase.request"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
