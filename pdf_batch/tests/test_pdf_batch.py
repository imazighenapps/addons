# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPdfBatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Batch Customer", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "Batch Product", "type": "service",
            "list_price": 100.0, "taxes_id": [(5, 0, 0)]})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1)

    def _invoice(self, price):
        return self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "journal_id": self.journal.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": self.product.id,
                "quantity": 1, "price_unit": price,
                "tax_ids": [(5, 0, 0)]})],
        })

    def test_01_totals(self):
        batch = self.env["pdf.batch"].create({
            "partner_id": self.partner.id,
            "invoice_ids": [(6, 0, [self._invoice(100.0).id,
                                    self._invoice(250.0).id])],
        })
        self.assertEqual(batch.invoice_count, 2)
        self.assertAlmostEqual(batch.total_amount, 350.0, places=2)

    def test_02_generate(self):
        batch = self.env["pdf.batch"].create({
            "partner_id": self.partner.id,
            "watermark": "COPY",
            "invoice_ids": [(6, 0, [self._invoice(100.0).id])],
        })
        batch.action_generate()
        self.assertEqual(batch.state, "done")
        self.assertTrue(batch.attachment_id)
        self.assertTrue(batch.attachment_id.raw)

    def test_03_requires_document(self):
        batch = self.env["pdf.batch"].create({"partner_id": self.partner.id})
        with self.assertRaises(Exception):
            batch.action_generate()

    def test_04_sequence(self):
        batch = self.env["pdf.batch"].create({"partner_id": self.partner.id})
        self.assertTrue(batch.name.startswith("BATCH/"))
