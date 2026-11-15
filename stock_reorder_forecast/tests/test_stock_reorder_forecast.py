# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockReorderForecast(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1).lot_stock_id
        if not cls.location:
            cls.location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        product_vals = {
            "name": "Forecast Product", "list_price": 10.0,
            "standard_price": 6.0,
        }
        if "is_storable" in cls.env["product.product"]._fields:
            product_vals.update({"type": "consu", "is_storable": True})
        else:
            product_vals["type"] = "product"
        cls.product = cls.env["product.product"].create(product_vals)
        cls.manager = cls._user(
            "rfc-manager", ["stock_reorder_forecast.group_stockreorder_user"])
        cls.outsider = cls._user("rfc-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _stock(self, qty):
        # Odoo 19 refuses a quant adjustment of exactly 0
        # ("Quantity or Reserved Quantity should be set").
        if not qty:
            return
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, qty)

    def _issue(self, qty):
        values = {
            "product_id": self.product.id,
            "product_uom_qty": qty,
            "location_id": self.location.id,
            "location_dest_id": self.customer_location.id,
        }
        if "product_uom" in self.env["stock.move"]._fields:
            values["product_uom"] = self.product.uom_id.id
        elif "product_uom_id" in self.env["stock.move"]._fields:
            values["product_uom_id"] = self.product.uom_id.id
        if "name" in self.env["stock.move"]._fields:
            values["name"] = "Forecast issue"
        elif "description_picking" in self.env["stock.move"]._fields:
            values["description_picking"] = "Forecast issue"
        move = self.env["stock.move"].create(values)
        move._action_confirm()
        move.quantity = qty
        move.picked = True
        move._action_done()
        return move

    def _run(self, **values):
        values.setdefault("location_id", self.location.id)
        wizard = self.env["stock.reorder.forecast"].create(values)
        wizard.action_run()
        return self.env["stock.reorder.suggestion"].search([
            ("location_id", "=", self.location.id),
            ("product_id", "=", self.product.id)])

    def test_01_suggestion_from_consumption(self):
        self._stock(70.0)
        self._issue(60.0)
        suggestions = self._run(lookback_days=90, horizon_days=30)
        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertAlmostEqual(suggestion.avg_daily, 0.667, places=3)
        self.assertEqual(suggestion.qty_available, 10.0)
        self.assertEqual(suggestion.suggested_qty, 10.0)

    def test_02_sufficient_stock_is_not_suggested(self):
        self._stock(500.0)
        self._issue(30.0)
        self.assertFalse(self._run(lookback_days=90, horizon_days=30))

    def test_03_incoming_covers_the_need(self):
        self._stock(60.0)
        self._issue(60.0)
        values = {
            "product_id": self.product.id,
            "product_uom_qty": 50.0,
            "location_id": self.customer_location.id,
            "location_dest_id": self.location.id,
        }
        if "product_uom" in self.env["stock.move"]._fields:
            values["product_uom"] = self.product.uom_id.id
        elif "product_uom_id" in self.env["stock.move"]._fields:
            values["product_uom_id"] = self.product.uom_id.id
        if "name" in self.env["stock.move"]._fields:
            values["name"] = "Incoming"
        elif "description_picking" in self.env["stock.move"]._fields:
            values["description_picking"] = "Incoming"
        move = self.env["stock.move"].create(values)
        move._action_confirm()
        self.assertFalse(self._run(lookback_days=90, horizon_days=30))

    def test_04_rerun_refreshes_the_open_suggestion(self):
        self._stock(60.0)
        self._issue(60.0)
        first = self._run(lookback_days=90, horizon_days=30)
        second = self._run(lookback_days=90, horizon_days=30)
        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)
        self.assertEqual(first, second)

    def test_05_states(self):
        self._stock(60.0)
        self._issue(60.0)
        suggestion = self._run()
        suggestion.action_ordered()
        self.assertEqual(suggestion.state, "ordered")
        with self.assertRaises(UserError):
            suggestion.action_ordered()
        suggestion.action_ignore()
        self.assertEqual(suggestion.state, "ignored")
        suggestion.action_reopen()
        self.assertEqual(suggestion.state, "open")

    def test_06_bad_window_is_refused(self):
        with self.assertRaises(UserError):
            self._run(lookback_days=0)

    def test_07_access_control(self):
        with self.assertRaises(Exception):
            self.env["stock.reorder.suggestion"].with_user(
                self.outsider).create({
                    "product_id": self.product.id,
                    "location_id": self.location.id,
                })
        self._stock(60.0)
        self._issue(60.0)
        suggestion = self._run()
        suggestion.with_user(self.manager).read()

    def test_08_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "RFC B"})
        foreign = self.env["stock.reorder.suggestion"].create({
            "product_id": self.product.id,
            "location_id": self.location.id,
            "company_id": company_b.id,
        })
        visible = self.env["stock.reorder.suggestion"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
