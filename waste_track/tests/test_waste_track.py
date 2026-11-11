# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWasteWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "WasteWatch Other Company"})

    def _stream(self, **values):
        defaults = {
            "name": "WasteWatch Test Oil Stream",
            "code": "OIL-01",
            "hazard_class": "hazardous",
            "contractor": "WasteWatch Contractor A",
        }
        defaults.update(values)
        return self.env["wst.stream"].create(defaults)

    def _collection(self, stream, **values):
        defaults = {
            "name": "WST-2026-001",
            "stream_id": stream.id,
            "collected_on": date(2026, 10, 5),
            "quantity": 120.0,
            "unit_name": "kg",
        }
        defaults.update(values)
        return self.env["wst.collection"].create(defaults)

    def test_01_defaults(self):
        stream = self._stream()
        col = self._collection(stream)
        self.assertEqual(col.state, "planned")
        self.assertEqual(stream.company_id, self.env.company)
        self.assertEqual(col.unit_name, "kg")

    def test_02_workflow(self):
        stream = self._stream(name="WasteWatch Test Paper")
        col = self._collection(stream, name="WST-2026-002")
        self.assertTrue(col.action_collect())
        col.receipt_no = "RCPT-2026-002"
        self.assertTrue(col.action_file())
        self.assertEqual(col.state, "filed")
        self.assertTrue(col.filed_on)

    def test_03_file_requires_receipt(self):
        stream = self._stream(name="WasteWatch Test Metal")
        col = self._collection(stream, name="WST-2026-003")
        col.action_collect()
        with self.assertRaises(ValidationError):
            col.action_file()

    def test_04_invalid_transitions(self):
        stream = self._stream(name="WasteWatch Test Glass")
        col = self._collection(stream, name="WST-2026-004")
        with self.assertRaises(ValidationError):
            col.action_file()
        col.action_collect()
        with self.assertRaises(ValidationError):
            col.action_collect()

    def test_05_quantity_and_dates(self):
        stream = self._stream(name="WasteWatch Test Qty")
        with self.assertRaises(ValidationError):
            self._collection(stream, name="WST-2026-005", quantity=0)
        with self.assertRaises(ValidationError):
            self._collection(stream, name="WST-2026-006",
                             collected_on=date(2026, 10, 5),
                             filed_on=date(2026, 10, 1))

    def test_06_counters(self):
        stream = self._stream(name="WasteWatch Test Counters")
        c1 = self._collection(stream, name="WST-2026-007A", quantity=50)
        c2 = self._collection(stream, name="WST-2026-007B", quantity=30)
        c1.action_collect()
        c1.receipt_no = "RCPT-A"
        c1.action_file()
        stream.invalidate_recordset()
        self.assertEqual(stream.collection_count, 2)
        self.assertEqual(stream.pending_receipt_count, 1)
        self.assertEqual(stream.total_quantity, 50)
        self.assertEqual(c2.state, "planned")

    def test_07_filed_cannot_reset(self):
        stream = self._stream(name="WasteWatch Test Reset")
        col = self._collection(stream, name="WST-2026-008")
        col.action_collect()
        col.receipt_no = "RCPT-2026-008"
        col.action_file()
        with self.assertRaises(ValidationError):
            col.action_reset()

    def test_08_company_isolation(self):
        stream = self._stream(name="WasteWatch Test Local")
        foreign = self.env["wst.stream"].with_company(
            self.other_company).sudo().create({
            "name": "WasteWatch Foreign Stream",
            "code": "FOR-01",
            "hazard_class": "non_hazardous",
            "company_id": self.other_company.id,
        })
        self.assertEqual(stream.company_id, self.env.company)
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(stream.company_id, foreign.company_id)
