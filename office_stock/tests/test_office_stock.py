# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOfficeStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "OfficeStock Other Company"})
        cls.requester = cls.env["res.partner"].create({
            "name": "OfficeStock Test Requester"})
        cls.supply = cls.env["office.supply"].create({
            "name": "OfficeStock Test Paper",
            "location": "Main Office",
            "on_hand_qty": 2,
            "min_qty": 5,
        })

    def _request(self, supply=None, **values):
        defaults = {
            "supply_id": (supply or self.supply).id,
            "requester_id": self.requester.id,
            "quantity": 3,
            "requested_on": date(2026, 11, 9),
        }
        defaults.update(values)
        return self.env["office.restock"].create(defaults)

    def test_01_supply_defaults_and_shortage(self):
        self.assertEqual(self.supply.company_id, self.env.company)
        self.assertEqual(self.supply.shortage_qty, 3)
        ok = self.env["office.supply"].create({
            "name": "OfficeStock Test Pens",
            "on_hand_qty": 10,
            "min_qty": 4,
        })
        self.assertEqual(ok.shortage_qty, 0)

    def test_02_request_defaults(self):
        req = self._request()
        self.assertEqual(req.state, "pending")
        self.assertEqual(req.company_id, self.env.company)
        self.assertTrue(req.name.startswith("Restock "))
        self.assertFalse(req.ordered_on)

    def test_03_mark_ordered_stamps_date(self):
        req = self._request()
        self.assertTrue(req.action_mark_ordered())
        self.assertEqual(req.state, "ordered")
        self.assertTrue(req.ordered_on)

    def test_04_double_order_is_refused(self):
        req = self._request()
        req.action_mark_ordered()
        with self.assertRaises(ValidationError):
            req.action_mark_ordered()

    def test_05_negative_quantities_are_refused(self):
        with self.assertRaises(ValidationError):
            self.env["office.supply"].create({
                "name": "OfficeStock Bad On Hand",
                "on_hand_qty": -1,
                "min_qty": 1,
            })
        with self.assertRaises(ValidationError):
            self.env["office.supply"].create({
                "name": "OfficeStock Bad Min",
                "on_hand_qty": 1,
                "min_qty": -1,
            })

    def test_06_requested_quantity_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._request(quantity=0)
        with self.assertRaises(ValidationError):
            self._request(quantity=-2)

    def test_07_ordered_before_requested_is_refused(self):
        with self.assertRaises(ValidationError):
            self._request(requested_on=date(2026, 11, 9),
                          ordered_on=date(2026, 11, 2))

    def test_08_supply_request_counters(self):
        open_req = self._request()
        closed = self._request(quantity=1)
        closed.action_mark_ordered()
        self.supply.invalidate_recordset()
        self.assertEqual(self.supply.request_count, 2)
        self.assertEqual(self.supply.open_request_count, 1)
        self.assertTrue(open_req)

    def test_09_company_isolation(self):
        foreign_supply = self.env["office.supply"].with_company(
            self.other_company).sudo().create({
            "name": "OfficeStock Foreign Supply",
            "on_hand_qty": 1,
            "min_qty": 2,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign_supply.company_id, self.other_company)
        self.assertNotEqual(foreign_supply.company_id, self.env.company)
        local = self._request()
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign_supply.company_id)
