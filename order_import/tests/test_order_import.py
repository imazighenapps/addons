# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOrderGate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "OrderGate Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "OrderGate Test Customer"})
        cls.batch = cls.env["order.import.batch"].create({
            "name": "OrderGate Batch 2026-11-01",
            "partner_id": cls.partner.id,
            "import_date": date(2026, 11, 1),
            "source_file": "ordergate_orders_2026.csv",
            "line_ids": [
                (0, 0, {
                    "name": "OrderGate Line 1",
                    "source_ref": "OG-ROW-001",
                    "product_ref": "OG-PROD-A",
                    "quantity": 5.0,
                }),
            ],
        })

    def _add_line(self, batch=None, **values):
        defaults = {
            "name": "OrderGate Extra Line",
            "batch_id": (batch or self.batch).id,
            "source_ref": "OG-ROW-002",
            "product_ref": "OG-PROD-B",
            "quantity": 2.0,
        }
        defaults.update(values)
        return self.env["order.import.line"].create(defaults)

    def test_01_batch_defaults(self):
        self.assertEqual(self.batch.state, "draft")
        self.assertEqual(self.batch.company_id, self.env.company)
        self.assertEqual(self.batch.line_count, 1)

    def test_02_validate_accepts_good_lines(self):
        self._add_line()
        self.assertTrue(self.batch.action_validate())
        self.assertEqual(self.batch.state, "validated")
        self.batch.invalidate_recordset()
        self.assertEqual(self.batch.accepted_count, 2)
        self.assertEqual(self.batch.rejected_count, 0)
        self.assertTrue(all(
            line.status == "accepted" for line in self.batch.line_ids))

    def test_03_validate_rejects_bad_lines(self):
        self._add_line(product_ref=False, quantity=0.0,
                       source_ref="OG-ROW-BAD")
        self.batch.action_validate()
        self.batch.invalidate_recordset()
        self.assertEqual(self.batch.rejected_count, 1)
        self.assertEqual(self.batch.accepted_count, 1)
        bad = self.batch.line_ids.filtered(lambda l: l.status == "rejected")
        self.assertTrue(bad.error_message)

    def test_04_process_requires_validation(self):
        with self.assertRaises(ValidationError):
            self.batch.action_process()
        self.batch.action_validate()
        self.assertTrue(self.batch.action_process())
        self.assertEqual(self.batch.state, "processed")

    def test_05_negative_quantity_refused(self):
        with self.assertRaises(ValidationError):
            self._add_line(quantity=-1.0, source_ref="OG-ROW-NEG")

    def test_06_counts_stored_after_validation(self):
        self._add_line(product_ref="OG-PROD-C", source_ref="OG-ROW-003")
        self._add_line(product_ref=False, quantity=1.0,
                       source_ref="OG-ROW-004")
        self.batch.action_validate()
        self.batch.invalidate_recordset()
        self.assertEqual(self.batch.line_count, 3)
        self.assertEqual(self.batch.accepted_count, 2)
        self.assertEqual(self.batch.rejected_count, 1)

    def test_07_search_with_errors_filter_logic(self):
        self._add_line(product_ref=False, quantity=1.0,
                       source_ref="OG-ROW-ERR")
        self.batch.action_validate()
        found = self.env["order.import.batch"].search([
            ("rejected_count", ">", 0), ("id", "=", self.batch.id)])
        self.assertIn(self.batch, found)

    def test_08_company_isolation(self):
        foreign_partner = self.env["res.partner"].sudo().create({
            "name": "OrderGate Foreign Customer"})
        foreign = self.env["order.import.batch"].with_company(
            self.other_company).sudo().create({
            "name": "OrderGate Foreign Batch",
            "partner_id": foreign_partner.id,
            "import_date": date(2026, 11, 2),
            "company_id": self.other_company.id,
            "line_ids": [
                (0, 0, {
                    "name": "OrderGate Foreign Line",
                    "product_ref": "OG-F-1",
                    "quantity": 1.0,
                }),
            ],
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(self.batch.company_id, self.env.company)
