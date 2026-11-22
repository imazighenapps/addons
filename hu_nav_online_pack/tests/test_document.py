# -*- coding: utf-8 -*-
import base64
from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHuNavDocument(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create({"name": "Client Test", "country_id": cls.env.ref("base.be").id})
        cls.product = cls.env["product.product"].create({"name": "Service", "type": "service", "list_price": 100.0})
        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": cls.partner.id,
            "invoice_line_ids": [Command.create({"product_id": cls.product.id, "quantity": 1, "price_unit": 100.0})],
        })
        cls.invoice.action_post()

    def test_generate_and_flow(self):
        doc = self.env["hu.nav.document"].create({"invoice_id": self.invoice.id, "company_id": self.company.id})
        doc.action_generate()
        self.assertEqual(doc.state, "ready")
        self.assertTrue(doc.file_data)
        self.assertTrue(doc.file_name)
        doc.action_mark_sent()
        self.assertEqual(doc.state, "sent")
