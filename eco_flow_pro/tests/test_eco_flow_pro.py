# -*- coding: utf-8 -*-
import unittest

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEcoFlowPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        bom_line_fields = cls.env["mrp.bom.line"]._fields
        if "product_id" not in bom_line_fields \
                or "product_qty" not in bom_line_fields \
                or "product_tmpl_id" not in cls.env["mrp.bom"]._fields:
            raise unittest.SkipTest("mrp BOM fields are missing.")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.tmpl = cls.env["product.template"].create({
            "name": "EcoFlowPro Test Table",
            "type": "consu",
            "is_storable": True,
        })
        cls.other_tmpl = cls.env["product.template"].create({
            "name": "EcoFlowPro Test Other Template",
            "type": "consu",
            "is_storable": True,
        })
        cls.comp_bolt = cls.env["product.product"].create({
            "name": "EcoFlowPro Test Bolt", "type": "consu",
            "is_storable": True,
        })
        cls.comp_nut = cls.env["product.product"].create({
            "name": "EcoFlowPro Test Nut", "type": "consu",
            "is_storable": True,
        })
        cls.comp_washer = cls.env["product.product"].create({
            "name": "EcoFlowPro Test Washer", "type": "consu",
            "is_storable": True,
        })
        cls.bom = cls.env["mrp.bom"].create({
            "product_tmpl_id": cls.tmpl.id,
            "uom_id": cls.uom_unit.id,
            "product_qty": 1.0,
        })
        cls.env["mrp.bom.line"].create({
            "bom_id": cls.bom.id,
            "product_id": cls.comp_bolt.id,
            "product_qty": 4.0,
        })
        cls.env["mrp.bom.line"].create({
            "bom_id": cls.bom.id,
            "product_id": cls.comp_nut.id,
            "product_qty": 4.0,
        })

    def _bom_qty(self, component):
        line = self.bom.bom_line_ids.filtered(
            lambda item: item.product_id == component)[:1]
        return line.product_qty if line else 0.0

    def _request(self):
        return self.env["eco.request"].create({
            "title": "EcoFlowPro Test Change",

            "product_tmpl_id": self.tmpl.id,
            "bom_id": self.bom.id,
        })

    def _full_request(self):
        request = self._request()
        self.env["eco.line"].create({
            "eco_id": request.id,
            "change_type": "change",
            "component_id": self.comp_bolt.id,
            "old_qty": 4.0,
            "new_qty": 6.0,
        })
        return request

    def _submitted(self, request):
        if request.state == "draft":
            request.action_submit()
        return request

    def _approved(self, request):
        self._submitted(request)
        if request.state == "review":
            request.action_approve()
        return request

    def test_01_submit_requires_lines(self):
        request = self._request()
        self.assertTrue(request.name.startswith("ECO/"))
        self.assertEqual(request.state, "draft")
        with self.assertRaises(UserError):
            request.action_submit()
        self.assertEqual(request.state, "draft")
        self.env["eco.line"].create({
            "eco_id": request.id,
            "change_type": "change",
            "component_id": self.comp_bolt.id,
            "old_qty": 4.0,
            "new_qty": 6.0,
        })
        self.assertEqual(request.line_count, 1)
        self.assertTrue(request.action_submit())
        self.assertEqual(request.state, "review")
        with self.assertRaises(UserError):
            request.action_submit()

    def test_02_approve_and_refuse(self):
        request = self._full_request()
        with self.assertRaises(UserError):
            request.action_approve()
        self._submitted(request)
        self.assertTrue(request.action_approve())
        self.assertEqual(request.state, "approved")
        self.assertEqual(request.approver_id, self.env.user)
        refused = self._submitted(self._full_request())
        self.assertTrue(refused.action_refuse())
        self.assertEqual(refused.state, "refused")
        self.assertEqual(refused.approver_id, self.env.user)
        with self.assertRaises(UserError):
            refused.action_approve()

    def test_03_apply_change_updates_quantity(self):
        request = self._full_request()
        self._approved(request)
        self.assertTrue(request.action_apply())
        self.assertEqual(request.state, "applied")
        self.assertEqual(self._bom_qty(self.comp_bolt), 6.0)
        self.assertEqual(self._bom_qty(self.comp_nut), 4.0)
        self.assertEqual(len(self.bom.bom_line_ids), 2)

    def test_04_apply_adds_bom_line(self):
        request = self._request()
        self.env["eco.line"].create({
            "eco_id": request.id,
            "change_type": "add",
            "component_id": self.comp_washer.id,
            "new_qty": 8.0,
        })
        self._approved(request)
        self.assertTrue(request.action_apply())
        self.assertEqual(request.state, "applied")
        self.assertEqual(len(self.bom.bom_line_ids), 3)
        self.assertEqual(self._bom_qty(self.comp_washer), 8.0)
        self.assertEqual(self._bom_qty(self.comp_bolt), 4.0)

    def test_05_apply_removes_bom_line(self):
        request = self._request()
        self.env["eco.line"].create({
            "eco_id": request.id,
            "change_type": "remove",
            "component_id": self.comp_bolt.id,
            "old_qty": 4.0,
        })
        self._approved(request)
        self.assertTrue(request.action_apply())
        self.assertEqual(request.state, "applied")
        self.assertEqual(len(self.bom.bom_line_ids), 1)
        self.assertEqual(
            self.bom.bom_line_ids.mapped("product_id"), self.comp_nut)

    def test_06_apply_requires_approval(self):
        request = self._full_request()
        with self.assertRaises(UserError):
            request.action_apply()
        self.assertEqual(request.state, "draft")
        request.action_submit()
        with self.assertRaises(UserError):
            request.action_apply()
        request.action_refuse()
        self.assertEqual(request.state, "refused")
        with self.assertRaises(UserError):
            request.action_apply()
        request.action_reset()
        request.action_submit()
        request.action_approve()
        self.assertTrue(request.action_apply())
        self.assertEqual(self._bom_qty(self.comp_bolt), 6.0)

    def test_07_reset_to_draft(self):
        request = self._request()
        with self.assertRaises(UserError):
            request.action_reset()
        refused = self._submitted(self._full_request())
        refused.action_refuse()
        self.assertTrue(refused.action_reset())
        self.assertEqual(refused.state, "draft")
        applied = self._approved(self._full_request())
        applied.action_apply()
        self.assertEqual(applied.state, "applied")
        with self.assertRaises(UserError):
            applied.write({"line_ids": [(5, 0, 0)]})
        self.assertTrue(applied.action_reset())
        self.assertEqual(applied.state, "draft")
        applied.line_ids.unlink()
        self.assertEqual(applied.line_count, 0)

    def test_08_constraints(self):
        request = self._request()
        values = {
            "eco_id": request.id,
            "change_type": "change",
            "component_id": self.comp_bolt.id,
            "new_qty": 2.0,
        }
        self.env["eco.line"].create(dict(values))
        with self.assertRaises(ValidationError):
            self.env["eco.line"].create(dict(values))
        with self.assertRaises(ValidationError):
            self.env["eco.line"].create({
                "eco_id": request.id,
                "change_type": "add",
                "component_id": self.comp_washer.id,
                "new_qty": 0.0,
            })
        with self.assertRaises(ValidationError):
            self.env["eco.line"].create({
                "eco_id": request.id,
                "change_type": "change",
                "component_id": self.comp_washer.id,
                "new_qty": -1.0,
            })
        with self.assertRaises(ValidationError):
            self.env["eco.request"].create({
                "title": "EcoFlowPro Test Wrong BOM",
                "product_tmpl_id": self.other_tmpl.id,
                "bom_id": self.bom.id,
            })
