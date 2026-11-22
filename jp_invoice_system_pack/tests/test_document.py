# -*- coding: utf-8 -*-
from odoo import Command
from odoo.exceptions import ValidationError, UserError
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestJpQualifyingInvoice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Client JP"})
        cls.product = cls.env["product.product"].create({"name": "Svc", "type": "service", "list_price": 100.0})
        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice", "partner_id": cls.partner.id,
            "invoice_line_ids": [Command.create({"product_id": cls.product.id, "quantity": 1, "price_unit": 100.0})],
        })
        cls.invoice.action_post()

    def test_register_and_compliant(self):
        rec = self.env["jp.qualifying.invoice"].create({
            "invoice_id": self.invoice.id, "company_id": self.env.company.id, "registration_number": "T1234567890123"})
        self.assertTrue(rec.compliance_ok)
        rec.action_register()
        self.assertEqual(rec.state, "registered")
        rec.action_mark_compliant()
        self.assertEqual(rec.state, "compliant")

    def test_invalid_registration(self):
        with self.assertRaises(ValidationError):
            self.env["jp.qualifying.invoice"].create({
                "invoice_id": self.invoice.id, "company_id": self.env.company.id, "registration_number": "BAD"})
