# -*- coding: utf-8 -*-
from odoo import Command
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestFactoringAssignment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Client F"})
        cls.product = cls.env["product.product"].create({"name": "S", "type": "service", "list_price": 1000.0})
        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice", "partner_id": cls.partner.id,
            "invoice_line_ids": [Command.create({"product_id": cls.product.id, "quantity": 1, "price_unit": 1000.0, "tax_ids": []})],
        })
        cls.invoice.action_post()

    def test_flow(self):
        rec = self.env["factoring.assignment"].create({
            "company_id": self.env.company.id, "factor_name": "Factor SA", "invoice_id": self.invoice.id,
            "advance_rate": 80.0, "commission_rate": 2.0, "retention_rate": 10.0})
        self.assertAlmostEqual(rec.advance_amount, 800.0, places=2)
        self.assertAlmostEqual(rec.commission_amount, 20.0, places=2)
        rec.action_assign(); rec.action_advance(); rec.action_release(); rec.action_close()
        self.assertEqual(rec.state, "closed")
        self.assertTrue(rec.released_amount >= 0)
