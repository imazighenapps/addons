# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo import Command
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestBillOfExchange(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Client LCR"})
        cls.product = cls.env["product.product"].create({"name": "P", "type": "service", "list_price": 500.0})
        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice", "partner_id": cls.partner.id,
            "invoice_line_ids": [Command.create({"product_id": cls.product.id, "quantity": 1, "price_unit": 500.0})],
        })
        cls.invoice.action_post()

    def test_flow(self):
        rec = self.env["bill.of.exchange"].create({
            "invoice_id": self.invoice.id, "amount": 500.0, "due_date": date.today() + timedelta(days=30),
            "discount_rate": 2.0, "company_id": self.env.company.id})
        self.assertAlmostEqual(rec.discount_amount, 10.0, places=2)
        self.assertAlmostEqual(rec.net_amount, 490.0, places=2)
        rec.action_portfolio()
        self.assertNotEqual(rec.name, "Nouveau")
        rec.action_domicile()
        rec.action_paid()
        self.assertEqual(rec.state, "paid")
