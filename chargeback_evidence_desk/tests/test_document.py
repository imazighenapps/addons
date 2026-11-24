# -*- coding: utf-8 -*-
from odoo import Command
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestChargebackCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Client CBK"})
        cls.product = cls.env["product.product"].create({"name": "P", "type": "service", "list_price": 80.0})
        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice", "partner_id": cls.partner.id,
            "invoice_line_ids": [Command.create({"product_id": cls.product.id, "quantity": 1, "price_unit": 80.0})],
        })
        cls.invoice.action_post()

    def test_flow(self):
        rec = self.env["chargeback.case"].create({
            "company_id": self.env.company.id, "invoice_id": self.invoice.id, "amount": 80.0, "reason": "Non reçu"})
        rec.action_assemble()
        self.assertEqual(rec.state, "assembled")
        self.assertTrue(rec.evidence_file)
        rec.action_submit()
        self.assertEqual(rec.state, "submitted")
