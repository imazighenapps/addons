# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAckWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "AckWatch Other Company"})
        cls.supplier = cls.env["res.partner"].create({
            "name": "AckWatch Test Supplier"})
        cls.order = cls.env["po.ack.order"].create({
            "name": "AckWatch PO-2026-001",
            "partner_id": cls.supplier.id,
            "sent_date": date(2026, 11, 1),
            "deadline_date": date(2026, 11, 10),
        })

    def _followup(self, **values):
        defaults = {
            "name": "AckWatch Follow-up",
            "ack_id": self.order.id,
            "followup_date": date(2026, 11, 3),
            "channel": "email",
            "response": "Supplier asked for more details.",
        }
        defaults.update(values)
        return self.env["po.ack.followup"].create(defaults)

    def test_01_order_defaults(self):
        self.assertEqual(self.order.state, "waiting")
        self.assertEqual(self.order.company_id, self.env.company)
        self.assertEqual(self.order.followup_count, 0)
        self.assertFalse(self.order.acknowledged_on)

    def test_02_followup_count(self):
        self._followup()
        self._followup(name="AckWatch Follow-up 2",
                       followup_date=date(2026, 11, 4),
                       channel="phone")
        self.order.invalidate_recordset()
        self.assertEqual(self.order.followup_count, 2)

    def test_03_acknowledge_sets_state(self):
        self.assertTrue(self.order.action_acknowledge())
        self.assertEqual(self.order.state, "acknowledged")
        self.assertTrue(self.order.acknowledged_on)
        self.assertFalse(self.order.is_overdue)

    def test_04_double_acknowledge_refused(self):
        self.order.action_acknowledge()
        with self.assertRaises(ValidationError):
            self.order.action_acknowledge()

    def test_05_deadline_before_sent_refused(self):
        with self.assertRaises(ValidationError):
            self.env["po.ack.order"].create({
                "name": "AckWatch Bad Dates",
                "partner_id": self.supplier.id,
                "sent_date": date(2026, 11, 10),
                "deadline_date": date(2026, 11, 1),
            })

    def test_06_overdue_flag_for_waiting_order(self):
        late = self.env["po.ack.order"].create({
            "name": "AckWatch PO-LATE-2026",
            "partner_id": self.supplier.id,
            "sent_date": fields.Date.today() - timedelta(days=10),
            "deadline_date": fields.Date.today() - timedelta(days=2),
        })
        self.assertTrue(late.is_overdue)
        self.assertGreaterEqual(late.days_waiting, 10)

    def test_07_future_followup_date_refused(self):
        future = date.today() + timedelta(days=5)
        with self.assertRaises(ValidationError):
            self._followup(followup_date=future)

    def test_08_company_isolation(self):
        foreign_supplier = self.env["res.partner"].sudo().create({
            "name": "AckWatch Foreign Supplier"})
        foreign = self.env["po.ack.order"].with_company(
            self.other_company).sudo().create({
            "name": "AckWatch PO-FOREIGN-2026",
            "partner_id": foreign_supplier.id,
            "sent_date": date(2026, 11, 2),
            "deadline_date": date(2026, 11, 12),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(self.order.company_id, self.env.company)

from odoo import fields  # noqa: E402
