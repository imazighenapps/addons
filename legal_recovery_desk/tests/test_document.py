# -*- coding: utf-8 -*-
from odoo import Command
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestLegalRecoveryCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Client L"})
        cls.product = cls.env["product.product"].create({"name": "P", "type": "service", "list_price": 700.0})
        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice", "partner_id": cls.partner.id,
            "invoice_line_ids": [Command.create({"product_id": cls.product.id, "quantity": 1, "price_unit": 700.0})],
        })
        cls.invoice.action_post()

    def test_flow(self):
        rec = self.env["legal.recovery.case"].create({
            "company_id": self.env.company.id, "invoice_id": self.invoice.id, "amount_claimed": 700.0})
        rec.action_start()
        self.assertEqual(rec.state, "ongoing")
        rec.recovered_amount = 700.0
        rec.action_win(); rec.action_close()
        self.assertEqual(rec.state, "closed")
