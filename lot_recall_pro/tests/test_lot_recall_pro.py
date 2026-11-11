# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRecallDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "RecallDesk Other Company"})
        cls.customer = cls.env["res.partner"].create({
            "name": "RecallDesk Test Customer 2026"})

    def _recall(self, **values):
        defaults = {
            "name": "RecallDesk Case 2026-01",
            "product_name": "RecallDesk Test Product",
            "reason": "Potential contamination found during routine check.",
            "start_date": date(2026, 3, 10),
        }
        defaults.update(values)
        recall = self.env["lot.recall"].create(defaults)
        self.env["lot.recall.line"].create({
            "recall_id": recall.id,
            "partner_id": self.customer.id,
            "lot_name": "LOT-2026-A",
            "quantity": 10.0,
            "reference": "WH/OUT/2026/001",
        })
        return recall

    def test_01_defaults_and_totals(self):
        recall = self._recall()
        self.assertEqual(recall.state, "draft")
        self.assertEqual(recall.company_id, self.env.company)
        self.assertEqual(recall.impact_count, 1)
        self.assertEqual(recall.notified_count, 0)
        self.assertEqual(recall.pending_count, 1)

    def test_02_activate_requires_lines(self):
        recall = self.env["lot.recall"].create({
            "name": "RecallDesk Empty 2026",
            "product_name": "Empty Product",
            "reason": "No lines yet.",
            "start_date": date(2026, 4, 1),
        })
        with self.assertRaises(UserError):
            recall.action_activate()

    def test_03_notify_and_close_flow(self):
        recall = self._recall(name="RecallDesk Flow 2026")
        recall.action_activate()
        recall.action_start_notifying()
        self.assertTrue(recall.action_mark_all_notified())
        recall.invalidate_recordset()
        self.assertEqual(recall.pending_count, 0)
        self.assertEqual(recall.notified_count, 1)
        self.assertTrue(recall.action_close())
        self.assertEqual(recall.state, "closed")

    def test_04_cannot_close_with_pending(self):
        recall = self._recall(name="RecallDesk Pending 2026")
        recall.action_activate()
        recall.action_start_notifying()
        with self.assertRaises(UserError):
            recall.action_close()

    def test_05_cancel_rules(self):
        recall = self._recall(name="RecallDesk Cancel 2026")
        self.assertTrue(recall.action_cancel())
        self.assertEqual(recall.state, "cancel")
        closed = self._recall(name="RecallDesk Closed 2026")
        closed.action_activate()
        closed.action_start_notifying()
        closed.action_mark_all_notified()
        closed.action_close()
        with self.assertRaises(UserError):
            closed.action_cancel()

    def test_06_line_quantity_constraint(self):
        recall = self._recall(name="RecallDesk Qty 2026")
        with self.assertRaises(ValidationError):
            self.env["lot.recall.line"].create({
                "recall_id": recall.id,
                "partner_id": self.customer.id,
                "lot_name": "LOT-2026-B",
                "quantity": 0.0,
            })

    def test_07_notified_line_requires_date(self):
        recall = self._recall(name="RecallDesk Notified Date 2026")
        with self.assertRaises(ValidationError):
            self.env["lot.recall.line"].create({
                "recall_id": recall.id,
                "partner_id": self.customer.id,
                "lot_name": "LOT-2026-C",
                "quantity": 1.0,
                "notified": True,
            })

    def test_08_totals_update_with_multiple_lines(self):
        recall = self._recall(name="RecallDesk Multi 2026")
        self.env["lot.recall.line"].create({
            "recall_id": recall.id,
            "partner_id": self.customer.id,
            "lot_name": "LOT-2026-D",
            "quantity": 3.0,
            "notified": True,
            "notified_on": date(2026, 3, 12),
        })
        recall.invalidate_recordset()
        self.assertEqual(recall.impact_count, 2)
        self.assertEqual(recall.notified_count, 1)
        self.assertEqual(recall.pending_count, 1)

    def test_09_company_isolation(self):
        foreign_customer = self.env["res.partner"].with_company(
            self.other_company).sudo().create({
            "name": "RecallDesk Foreign Customer 2026"})
        foreign = self.env["lot.recall"].with_company(
            self.other_company).sudo().create({
            "name": "Foreign Recall 2026",
            "product_name": "Foreign Product",
            "reason": "Foreign reason",
            "start_date": date(2026, 5, 1),
            "company_id": self.other_company.id,
        })
        self.env["lot.recall.line"].with_company(
            self.other_company).sudo().create({
            "recall_id": foreign.id,
            "partner_id": foreign_customer.id,
            "lot_name": "LOT-F-2026",
            "quantity": 1.0,
        })
        local = self._recall(name="RecallDesk Local 2026")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
