# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVatCross(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "VATCross Other Company"})
        cls.check = cls.env["vat.check"].create({
            "name": "VATCross 2026-01",
            "period_start": date(2026, 1, 1),
            "period_end": date(2026, 1, 31),
        })

    def _line(self, check=None, **values):
        defaults = {
            "check_id": (check or self.check).id,
            "box_name": "Box 01",
            "reported_amount": 1000.0,
            "ledger_amount": 1000.0,
        }
        defaults.update(values)
        return self.env["vat.check.line"].create(defaults)

    def test_01_check_defaults(self):
        self.assertEqual(self.check.state, "draft")
        self.assertEqual(self.check.company_id, self.env.company)
        self.assertFalse(self.check.closed_on)

    def test_02_difference_is_computed(self):
        line = self._line(box_name="Box 54", reported_amount=1250.0,
                          ledger_amount=1200.0)
        self.assertAlmostEqual(line.difference_amount, 50.0, places=2)
        self.assertIn("Box 54", line.name)

    def test_03_review_and_close_workflow(self):
        line = self._line(box_name="Box 59")
        self.assertTrue(self.check.action_start_review())
        self.assertEqual(self.check.state, "review")
        self.assertTrue(line.action_mark_reviewed())
        self.assertTrue(self.check.action_close())
        self.assertEqual(self.check.state, "closed")
        self.assertTrue(self.check.closed_on)

    def test_04_close_without_review_is_refused(self):
        self._line(box_name="Box 81")
        self.check.action_start_review()
        with self.assertRaises(ValidationError):
            self.check.action_close()

    def test_05_difference_needs_explanation(self):
        line = self._line(box_name="Box 82", reported_amount=300.0,
                          ledger_amount=250.0)
        with self.assertRaises(ValidationError):
            line.action_mark_reviewed()

    def test_06_period_end_before_start_is_refused(self):
        with self.assertRaises(ValidationError):
            self.env["vat.check"].create({
                "name": "VATCross Bad Period",
                "period_start": date(2026, 6, 30),
                "period_end": date(2026, 6, 1),
            })

    def test_07_progress_counters(self):
        reviewed = self._line(box_name="Box 83")
        reviewed.action_mark_reviewed()
        open_line = self._line(box_name="Box 84", reported_amount=500.0,
                               ledger_amount=450.0)
        self.check.invalidate_recordset()
        self.assertEqual(self.check.line_count, 2)
        self.assertEqual(self.check.open_line_count, 1)
        self.assertTrue(open_line)

    def test_08_company_isolation(self):
        foreign = self.env["vat.check"].with_company(
            self.other_company).sudo().create({
            "name": "VATCross Foreign",
            "period_start": date(2026, 7, 1),
            "period_end": date(2026, 7, 31),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self.env["vat.check"].create({
            "name": "VATCross Local",
            "period_start": date(2026, 8, 1),
            "period_end": date(2026, 8, 31),
        })
        self.assertEqual(local.company_id, self.env.company)
