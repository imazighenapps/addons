# -*- coding: utf-8 -*-
from odoo import Command
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestCollectionAgencyCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Client D"})
        cls.product = cls.env["product.product"].create({"name": "P", "type": "service", "list_price": 400.0})
        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice", "partner_id": cls.partner.id,
            "invoice_line_ids": [Command.create({"product_id": cls.product.id, "quantity": 1, "price_unit": 400.0})],
        })
        cls.invoice.action_post()

    def test_flow(self):
        rec = self.env["collection.agency.case"].create({
            "company_id": self.env.company.id, "agency_name": "Recov SA", "invoice_id": self.invoice.id,
            "amount_due": 400.0, "commission_rate": 10.0})
        rec.action_send()
        self.assertEqual(rec.state, "sent")
        self.assertTrue(rec.export_file)
        rec.recovered_amount = 400.0
        rec.action_register_recovery()
        self.assertEqual(rec.state, "recovered")
        self.assertAlmostEqual(rec.commission_amount, 40.0, places=2)
