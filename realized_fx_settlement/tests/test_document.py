# -*- coding: utf-8 -*-
from odoo import Command
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestRealizedFx(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "P"})
        cls.product = cls.env["product.product"].create({"name": "S", "type": "service", "list_price": 100.0})
        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice", "partner_id": cls.partner.id,
            "invoice_line_ids": [Command.create({"product_id": cls.product.id, "quantity": 1, "price_unit": 100.0})],
        })
        cls.invoice.action_post()

    def test_compute(self):
        rec = self.env["realized.fx.settlement"].create({
            "company_id": self.env.company.id, "invoice_id": self.invoice.id,
            "amount_currency": 100.0, "invoice_rate": 1.0, "settlement_rate": 1.1})
        rec.action_compute()
        self.assertEqual(rec.state, "computed")
        self.assertNotEqual(rec.fx_gain_loss, 0.0)
