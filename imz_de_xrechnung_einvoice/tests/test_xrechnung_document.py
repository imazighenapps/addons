# -*- coding: utf-8 -*-
import base64
from lxml import etree
from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestXRechnungDocument(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write({"vat": "DE123456789"})
        cls.partner = cls.env["res.partner"].create({"name": "Kunde DE", "country_id": cls.env.ref("base.de").id})
        cls.product = cls.env["product.product"].create({"name": "Dienst", "type": "service", "list_price": 50.0})
        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": cls.partner.id,
            "invoice_line_ids": [Command.create({"product_id": cls.product.id, "quantity": 1, "price_unit": 50.0})],
        })
        cls.invoice.action_post()

    def test_generate(self):
        doc = self.env["xrechnung.document"].create({
            "invoice_id": self.invoice.id, "company_id": self.company.id})
        doc.action_generate()
        self.assertEqual(doc.state, "ready")
        raw = bytes(doc.file_data or b"")
        if raw[:1] != b"<" and not raw.startswith(b"\xef\xbb\xbf"):
            raw = base64.b64decode(raw)
        xml = etree.fromstring(raw)
        self.assertIn("CrossIndustryInvoice", xml.tag)
