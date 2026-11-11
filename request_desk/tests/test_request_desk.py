# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPRDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "PRDesk Other Company"})
        cls.requester = cls.env.ref("base.user_admin")

    def _request(self, **values):
        defaults = {
            "name": "PRDesk Test Request 2026",
            "requester_id": self.requester.id,
            "needed_on": date(2026, 4, 15),
        }
        defaults.update(values)
        request = self.env["pr.request"].create(defaults)
        self.env["pr.request.line"].create({
            "request_id": request.id,
            "product_name": "PRDesk Test Paper",
            "description": "A4 white paper",
            "quantity": 5.0,
            "uom_name": "box",
        })
        return request

    def test_01_request_defaults(self):
        request = self._request()
        self.assertEqual(request.state, "draft")
        self.assertEqual(request.company_id, self.env.company)
        self.assertEqual(request.line_count, 1)
        self.assertEqual(request.total_qty, 5.0)

    def test_02_submit_and_approve(self):
        request = self._request()
        self.assertTrue(request.action_submit())
        self.assertEqual(request.state, "submitted")
        self.assertTrue(request.action_approve())
        self.assertEqual(request.state, "approved")

    def test_03_submit_requires_line(self):
        request = self.env["pr.request"].create({
            "name": "PRDesk Empty Request 2026",
            "requester_id": self.requester.id,
            "needed_on": date(2026, 5, 1),
        })
        with self.assertRaises(UserError):
            request.action_submit()

    def test_04_order_and_done_flow(self):
        request = self._request(name="PRDesk Flow 2026")
        request.action_submit()
        request.action_approve()
        self.assertTrue(request.action_mark_ordered())
        self.assertEqual(request.state, "ordered")
        self.assertTrue(request.action_done())
        self.assertEqual(request.state, "done")

    def test_05_cancel_and_reset(self):
        request = self._request(name="PRDesk Cancel 2026")
        request.action_submit()
        self.assertTrue(request.action_reset_draft())
        self.assertEqual(request.state, "draft")
        request.action_submit()
        self.assertTrue(request.action_cancel())
        self.assertEqual(request.state, "cancel")
        self.assertTrue(request.action_reset_draft())
        self.assertEqual(request.state, "draft")

    def test_06_ordered_cannot_be_cancelled(self):
        request = self._request(name="PRDesk Ordered 2026")
        request.action_submit()
        request.action_approve()
        request.action_mark_ordered()
        with self.assertRaises(UserError):
            request.action_cancel()

    def test_07_line_quantity_must_be_positive(self):
        request = self._request(name="PRDesk Qty 2026")
        line = request.line_ids[0]
        with self.assertRaises(ValidationError):
            line.quantity = 0
        with self.assertRaises(ValidationError):
            line.quantity = -1

    def test_08_totals_update(self):
        request = self._request(name="PRDesk Totals 2026")
        self.env["pr.request.line"].create({
            "request_id": request.id,
            "product_name": "PRDesk Test Ink",
            "quantity": 2.0,
        })
        request.invalidate_recordset()
        self.assertEqual(request.line_count, 2)
        self.assertEqual(request.total_qty, 7.0)

    def test_09_company_isolation(self):
        foreign_user = self.env["res.users"].with_company(
            self.other_company).sudo().create({
            "name": "PRDesk Foreign User",
            "login": "prdesk_foreign_user_2026@example.com",
            "company_id": self.other_company.id,
            "company_ids": [(6, 0, [self.other_company.id])],
        })
        foreign = self.env["pr.request"].with_company(
            self.other_company).sudo().create({
            "name": "PRDesk Foreign 2026",
            "requester_id": foreign_user.id,
            "needed_on": date(2026, 6, 1),
            "company_id": self.other_company.id,
        })
        self.env["pr.request.line"].with_company(
            self.other_company).sudo().create({
            "request_id": foreign.id,
            "product_name": "Foreign item",
            "quantity": 1.0,
        })
        local = self._request(name="PRDesk Local 2026")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
