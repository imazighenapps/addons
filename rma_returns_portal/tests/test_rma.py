# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRma(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({
            "name": "Demo Headphones", "type": "consu", "list_price": 120.0,
        })
        cls.partner = cls.env["res.partner"].create({"name": "Web Customer"})
        cls.order = cls.env["sale.order"].create({
            "partner_id": cls.partner.id,
            "order_line": [(0, 0, {
                "product_id": cls.product.id, "product_uom_qty": 2.0,
                "price_unit": 120.0,
            })],
        })
        cls.order.action_confirm()
        picking = cls.order.picking_ids
        picking.move_ids.quantity = 2.0
        picking.button_validate()
        cls.picking = picking
        cls.reason = cls.env.ref("rma_returns_portal.reason_withdrawal")

    def _make_rma(self, qty=1.0, rtype="withdrawal"):
        line = self.order.order_line
        return self.env["rma.request"].create({
            "partner_id": self.partner.id,
            "sale_order_id": self.order.id,
            "picking_id": self.picking.id,
            "request_type": rtype,
            "reason_id": self.reason.id,
            "line_ids": [(0, 0, {
                "sale_line_id": line.id,
                "product_id": self.product.id,
                "qty_delivered": 2.0,
                "qty_requested": qty,
                "price_unit": 120.0,
            })],
        })

    def test_01_seed(self):
        self.assertEqual(len(self.env["rma.reason"].search([])), 3)
        self.assertEqual(len(self.env["rma.grade"].search([])), 4)

    def test_02_qty_guard(self):
        rma = self._make_rma(qty=5.0)
        with self.assertRaises(UserError):
            rma.action_submit()

    def test_03_non_returnable(self):
        self.product.product_tmpl_id.is_returnable = False
        rma = self._make_rma()
        with self.assertRaises(UserError):
            rma.action_submit()
        self.product.product_tmpl_id.is_returnable = True

    def test_04_approve_creates_return(self):
        rma = self._make_rma()
        rma.action_submit()
        self.assertEqual(rma.state, "submitted")
        rma.action_approve()
        self.assertEqual(rma.state, "approved")
        self.assertTrue(rma.return_created)
        self.assertEqual(len(rma.return_picking_ids), 1)

    def test_05_qc_required(self):
        rma = self._make_rma()
        rma.action_submit()
        rma.action_approve()
        with self.assertRaises(UserError):
            rma.action_qc_done()
        grade = self.env.ref("rma_returns_portal.grade_a")
        rma.line_ids.grade_id = grade.id
        rma.action_qc_done()
        self.assertEqual(rma.state, "qc_done")

    def test_06_resolve_credit(self):
        rma = self._make_rma()
        rma.action_submit()
        rma.action_resolve_credit()
        self.assertEqual(rma.state, "resolved")
        self.assertEqual(rma.resolution, "credit")
