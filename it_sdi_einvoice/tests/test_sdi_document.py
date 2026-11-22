# -*- coding: utf-8 -*-
"""Tests fonctionnels SdI (génération FatturaPA et statuts)."""
import base64

from lxml import etree

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSdiDocument(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write({"vat": "IT01234567890"})
        cls.partner = cls.env["res.partner"].create({
            "name": "Cliente IT", "country_id": cls.env.ref("base.it").id,
        })
        cls.product = cls.env["product.product"].create({
            "name": "Servizio", "type": "service", "list_price": 100.0,
        })
        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": cls.partner.id,
            "invoice_line_ids": [Command.create({
                "product_id": cls.product.id,
                "quantity": 2,
                "price_unit": 100.0,
            })],
        })
        cls.invoice.action_post()

    def _doc(self, **kw):
        vals = dict(invoice_id=self.invoice.id,
                    destinatario_code="XXXXXXX", company_id=self.company.id)
        vals.update(kw)
        return self.env["sdi.document"].create(vals)

    def test_generate_xml_and_structure(self):
        doc = self._doc(destinatario_code="ABCDEF1")
        doc.action_prepare()
        self.assertEqual(doc.state, "ready")
        self.assertTrue(doc.file_name.endswith(".xml"))
        raw = bytes(doc.file_data or b"")
        if raw[:1] != b"<" and not raw.startswith(b"\xef\xbb\xbf"):
            raw = base64.b64decode(raw)
        xml = etree.fromstring(raw)
        self.assertIn("FatturaElettronica", xml.tag)
        self.assertIn("ABCDEF1", etree.tostring(xml).decode())

    def test_status_flow_and_reject(self):
        doc = self._doc()
        doc.action_prepare()
        doc.action_mark_sent()
        self.assertEqual(doc.state, "sent")
        doc.last_error = "Errore test"
        doc.action_mark_rejected()
        self.assertEqual(doc.state, "rejected")
        self.assertIn("refusé", (doc.status_note or "").lower())

    def test_destinatario_constraint(self):
        with self.assertRaises(ValidationError):
            self._doc(destinatario_code="SHORT")
