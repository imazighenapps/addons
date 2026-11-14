# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReturnFlowPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "ReturnFlow Test Customer"})
        cls.product = cls.env["product.product"].create({
            "name": "ReturnFlow Test Product",
            "type": "consu",
        })
        cls.reason = cls.env["return.flow.reason"].create({
            "name": "Damaged on arrival"})
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1)
        cls.picking_type = cls.env["stock.picking.type"].search(
            [("code", "=", "outgoing"),
             ("warehouse_id", "=", cls.warehouse.id)], limit=1)
        cls.picking = cls.env["stock.picking"].create({
            "picking_type_id": cls.picking_type.id,
            "partner_id": cls.partner.id,
            "location_id": cls.picking_type.default_location_src_id.id,
            "location_dest_id":
                cls.picking_type.default_location_dest_id.id,
        })
        cls.move = cls.env["stock.move"].create(
            cls._move_vals(cls.picking, cls.picking_type, cls.product, 5.0))
        cls.picking.action_confirm()
        cls._set_done_qty(cls.move, 5.0)
        cls.picking.button_validate()

        cls.manager = cls._user(
            "returnflow-manager", ["return_flow_pro.group_returnflowpr_user"])
        cls.outsider = cls._user(
            "returnflow-outsider", ["base.group_user"])

    @classmethod
    def _move_vals(cls, picking, picking_type, product, qty):
        vals = {
            "picking_id": picking.id,
            "product_id": product.id,
            "product_uom_qty": qty,
            "picking_type_id": picking_type.id,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": picking_type.default_location_dest_id.id,
        }
        if "name" in cls.env["stock.move"]._fields:
            vals["name"] = product.display_name
        return vals

    @classmethod
    def _set_done_qty(cls, move, qty):
        if "quantity" in move._fields:
            move.quantity = qty
        elif "quantity_done" in move._fields:
            move.quantity_done = qty

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

    def _make_return(self):
        req = self.env["return.flow.request"].create({
            "picking_id": self.picking.id,
            "partner_id": self.partner.id,
            "reason_id": self.reason.id,
            "line_ids": [(0, 0, {
                "move_id": self.move.id,
                "product_id": self.product.id,
                "qty_delivered": 5.0,
                "qty": 2.0,
                "product_uom": self.product.uom_id.id,
            })],
        })
        return req

    def test_01_create_and_workflow(self):
        req = self._make_return()
        self.assertEqual(req.state, "requested")
        self.assertAlmostEqual(req.total_qty, 2.0)
        req.action_receive()
        self.assertEqual(req.state, "received")
        self.assertTrue(req.date_received)
        req.action_inspect()
        self.assertEqual(req.state, "inspected")
        req.action_restock()
        self.assertEqual(req.state, "restocked")
        self.assertEqual(req.outcome, "restock")

    def test_02_qty_cannot_exceed_delivered(self):
        req = self._make_return()
        with self.assertRaises(ValidationError):
            req.line_ids.write({"qty": 6.0})

    def test_03_credit_note_created(self):
        req = self._make_return()
        req.action_receive()
        req.action_inspect()
        action = req.action_create_credit_note()
        self.assertTrue(req.credit_move_id)
        self.assertEqual(req.credit_move_id.move_type, "out_refund")
        self.assertEqual(action["res_id"], req.credit_move_id.id)
        # second call returns the same note
        action2 = req.action_create_credit_note()
        self.assertEqual(action2["res_id"], req.credit_move_id.id)

    def test_04_repair_and_scrap_outcomes(self):
        req = self._make_return()
        req.action_receive()
        req.action_inspect()
        req.action_repair()
        self.assertEqual(req.state, "repaired")
        req2 = self.env["return.flow.request"].create({
            "picking_id": self.picking.id,
            "partner_id": self.partner.id,
            "reason_id": self.reason.id,
            "line_ids": [(0, 0, {
                "move_id": self.move.id,
                "product_id": self.product.id,
                "qty_delivered": 5.0,
                "qty": 1.0,
                "product_uom": self.product.uom_id.id,
            })],
        })
        req2.action_receive()
        req2.action_inspect()
        req2.action_scrap()
        self.assertEqual(req2.state, "scrapped")

    def test_05_cancel_not_after_close(self):
        req = self._make_return()
        req.action_receive()
        req.action_inspect()
        req.action_restock()
        with self.assertRaises(UserError):
            req.action_cancel()

    def test_06_access_control(self):
        req = self._make_return()
        with self.assertRaises(Exception):
            self.env["return.flow.request"].with_user(
                self.outsider).create({
                    "picking_id": self.picking.id,
                    "partner_id": self.partner.id,
                    "reason_id": self.reason.id,
                    "line_ids": [(0, 0, {
                        "move_id": self.move.id,
                        "product_id": self.product.id,
                        "qty_delivered": 5.0,
                        "qty": 1.0,
                        "product_uom": self.product.uom_id.id,
                    })],
                })
        req.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "ReturnFlow B"})
        foreign = self.env["return.flow.request"].create({
            "picking_id": self.picking.id,
            "partner_id": self.partner.id,
            "reason_id": self.reason.id,
            "company_id": company_b.id,
            "line_ids": [(0, 0, {
                "move_id": self.move.id,
                "product_id": self.product.id,
                "qty_delivered": 5.0,
                "qty": 1.0,
                "product_uom": self.product.uom_id.id,
            })],
        })
        visible = self.env["return.flow.request"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
