# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRecodeDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "RecodeDesk Other Company"})

    def _request(self, **values):
        defaults = {
            "name": "RCD-TEST-001",
            "old_code": "OLD-100",
            "new_code": "NEW-200",
            "reason": "Renumbering",
            "planned_on": date(2026, 8, 1),
        }
        defaults.update(values)
        return self.env["recode.request"].create(defaults)

    def _line(self, req, **values):
        defaults = {
            "request_id": req.id,
            "source": "Label",
            "old_value": req.old_code,
        }
        defaults.update(values)
        return self.env["recode.line"].create(defaults)

    def test_01_defaults(self):
        req = self._request()
        self.assertEqual(req.state, "draft")
        self.assertEqual(req.company_id, self.env.company)
        self.assertEqual(req.line_count, 0)
        self.assertFalse(req.applied_on)

    def test_02_apply_updates_lines_and_stamps_date(self):
        req = self._request(name="RCD-APPLY")
        self._line(req, source="Label")
        self._line(req, source="Spreadsheet")
        self.assertTrue(req.action_apply())
        self.assertEqual(req.state, "done")
        self.assertTrue(req.applied_on)
        req.invalidate_recordset(["line_count", "updated_count"])
        self.assertEqual(req.updated_count, 2)
        self.assertTrue(all(req.line_ids.mapped("updated")))

    def test_03_apply_requires_lines(self):
        req = self._request(name="RCD-NOLINES")
        with self.assertRaises(UserError):
            req.action_apply()

    def test_04_same_code_refused(self):
        with self.assertRaises(ValidationError):
            self._request(name="RCD-SAME", old_code="A1", new_code="A1")

    def test_05_applied_request_locked(self):
        req = self._request(name="RCD-LOCK")
        line = self._line(req, source="Label")
        req.action_apply()
        with self.assertRaises(UserError):
            self._line(req, source="Late")
        with self.assertRaises(UserError):
            line.write({"source": "Changed"})

    def test_06_reset_draft(self):
        req = self._request(name="RCD-RESET")
        self._line(req)
        req.action_apply()
        self.assertTrue(req.action_reset_draft())
        self.assertEqual(req.state, "draft")
        self.assertFalse(req.applied_on)
        self.assertFalse(any(req.line_ids.mapped("updated")))

    def test_07_line_new_value_differs(self):
        req = self._request(name="RCD-LINEVAL")
        with self.assertRaises(ValidationError):
            self._line(req, old_value="X", new_value="X")

    def test_08_counts_stored(self):
        req = self._request(name="RCD-COUNT")
        self._line(req, source="A")
        self._line(req, source="B")
        req.invalidate_recordset(["line_count", "updated_count"])
        self.assertEqual(req.line_count, 2)
        self.assertEqual(req.updated_count, 0)

    def test_09_company_isolation(self):
        foreign = self.env["recode.request"].with_company(
            self.other_company).create({
            "name": "RCD-FOREIGN",
            "old_code": "F-OLD",
            "new_code": "F-NEW",
            "reason": "Foreign",
            "planned_on": date(2026, 9, 1),
            "company_id": self.other_company.id,
        })
        local = self._request(name="RCD-LOCAL")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(local.company_id, foreign.company_id)
