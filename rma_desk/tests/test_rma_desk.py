# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReturnDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ReturnDesk Other Company"})

    def _request(self, **values):
        defaults = {
            "name": "ReturnDesk RMA 2026-08",
            "customer_name": "ReturnDesk Customer A",
            "requested_on": date(2026, 8, 12),
            "reason": "Damaged packaging reported by customer.",
        }
        defaults.update(values)
        return self.env["rma.request"].create(defaults)

    def _line(self, request, **values):
        defaults = {
            "request_id": request.id,
            "product_name": "ReturnDesk Item A",
            "quantity": 2.0,
            "unit_value": 50.0,
        }
        defaults.update(values)
        return self.env["rma.line"].create(defaults)

    def test_01_request_defaults(self):
        req = self._request()
        self.assertEqual(req.state, "draft")
        self.assertEqual(req.company_id, self.env.company)
        self.assertEqual(req.line_count, 0)
        self.assertEqual(req.total_qty, 0.0)

    def test_02_line_subtotal_and_totals(self):
        req = self._request()
        line = self._line(req)
        self.assertEqual(line.subtotal, 100.0)
        req.invalidate_recordset()
        self.assertEqual(req.line_count, 1)
        self.assertEqual(req.total_qty, 2.0)
        self.assertEqual(req.total_value, 100.0)

    def test_03_approve_receive_resolve_workflow(self):
        req = self._request()
        self._line(req)
        self.assertTrue(req.action_approve())
        self.assertEqual(req.state, "approved")
        self.assertTrue(req.action_receive())
        self.assertEqual(req.state, "received")
        req.resolution = "credit"
        req.credit_amount = 100.0
        self.assertTrue(req.action_resolve())
        self.assertEqual(req.state, "resolved")

    def test_04_approve_without_lines_is_refused(self):
        req = self._request()
        with self.assertRaises(UserError):
            req.action_approve()

    def test_05_resolve_requires_received_and_resolution(self):
        req = self._request()
        self._line(req)
        with self.assertRaises(UserError):
            req.action_resolve()
        req.action_approve()
        req.action_receive()
        with self.assertRaises(UserError):
            req.action_resolve()

    def test_06_refuse_from_draft_and_approved(self):
        req = self._request(name="ReturnDesk RMA 2026-09")
        self._line(req)
        req.action_refuse()
        self.assertEqual(req.state, "refused")
        req2 = self._request(name="ReturnDesk RMA 2026-09B",
                             requested_on=date(2026, 9, 2))
        self._line(req2, product_name="ReturnDesk Item B")
        req2.action_approve()
        req2.action_refuse()
        self.assertEqual(req2.state, "refused")

    def test_07_line_quantity_must_be_positive(self):
        req = self._request(name="ReturnDesk RMA 2026-10",
                            requested_on=date(2026, 10, 3))
        with self.assertRaises(ValidationError):
            self._line(req, quantity=0.0)
        with self.assertRaises(ValidationError):
            self._line(req, quantity=-1.0)

    def test_08_negative_values_are_refused(self):
        req = self._request(name="ReturnDesk RMA 2026-11",
                            requested_on=date(2026, 11, 4))
        with self.assertRaises(ValidationError):
            self._line(req, unit_value=-10.0)
        with self.assertRaises(ValidationError):
            req.credit_amount = -5.0

    def test_09_company_isolation(self):
        foreign = self.env["rma.request"].with_company(
            self.other_company).sudo().create({
            "name": "ReturnDesk Foreign RMA",
            "customer_name": "ReturnDesk Foreign Customer",
            "requested_on": date(2027, 2, 1),
            "reason": "Foreign return reason.",
            "company_id": self.other_company.id,
        })
        local = self._request(name="ReturnDesk Local RMA 2027-02",
                              requested_on=date(2027, 2, 1))
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
