# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMergeDocs(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Dossier Customer", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "Dossier Product", "type": "consu",
            "list_price": 80.0, "taxes_id": [(5, 0, 0)]})
        cls.order = cls.env["sale.order"].create({
            "partner_id": cls.partner.id,
            "order_line": [(0, 0, {
                "product_id": cls.product.id, "product_uom_qty": 2,
                "price_unit": 80.0})]})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1)
        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": cls.partner.id,
            "journal_id": cls.journal.id,
            "invoice_date": date.today(),
            "invoice_line_ids": [(0, 0, {
                "product_id": cls.product.id, "quantity": 1,
                "price_unit": 80.0, "tax_ids": [(5, 0, 0)]})]})

    def _merge(self):
        return self.env["doc.merge"].create({
            "partner_id": self.partner.id,
            "include_deliveries": False,
        })

    def test_01_load_documents(self):
        merge = self._merge()
        merge.action_load()
        self.assertEqual(merge.document_count, 2)
        self.assertEqual(merge.state, "loaded")
        self.assertAlmostEqual(merge.total_amount, 240.0, places=2)

    def test_02_snapshot_contains_product(self):
        merge = self._merge()
        merge.action_load()
        self.assertIn("Dossier Product", merge.line_ids[0].snapshot_html)

    def test_03_generate(self):
        merge = self._merge()
        merge.action_load()
        merge.action_generate()
        self.assertEqual(merge.state, "done")
        self.assertTrue(merge.attachment_id)
        self.assertTrue(merge.attachment_id.raw)

    def test_04_no_document_found(self):
        partner = self.env["res.partner"].create({"name": "Empty Customer"})
        merge = self.env["doc.merge"].create({
            "partner_id": partner.id,
            "include_deliveries": False,
        })
        with self.assertRaises(Exception):
            merge.action_load()

    def test_05_sequence(self):
        merge = self._merge()
        self.assertTrue(merge.name.startswith("DOS/"))
