# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo import fields


class TestVendorCollaboration(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor A", "supplier_rank": 1})
        cls.product = cls.env["product.product"].create({"name": "Component", "type": "consu", "is_storable": True})

    def test_asn_flow(self):
        asn = self.env["vendor.asn"].create({
            "partner_id": self.vendor.id,
            "expected_date": fields.Date.today(),
            "line_ids": [(0, 0, {"product_id": self.product.id, "qty_expected": 5})],
        })
        asn.action_submit()
        asn.action_receive()
        self.assertEqual(asn.state, "received")

    def test_chargeback_and_catalog(self):
        cb = self.env["vendor.chargeback"].create({
            "partner_id": self.vendor.id,
            "reason": "quality",
            "amount": 50.0,
        })
        cb.action_submit()
        cb.action_approve()
        cb.action_resolve()
        self.assertEqual(cb.state, "resolved")
        item = self.env["vendor.catalog.item"].create({
            "partner_id": self.vendor.id,
            "product_id": self.product.id,
            "price": 10.0,
            "lead_time_days": 3,
        })
        item.action_activate()
        self.assertEqual(item.state, "active")
