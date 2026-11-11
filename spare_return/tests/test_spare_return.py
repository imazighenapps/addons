# -*- coding: utf-8 -*-
from datetime import date

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSpareBack(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "SpareBack Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "SpareBack Customer Alpha"})
        cls.partner_b = cls.env["res.partner"].create({
            "name": "SpareBack Customer Beta"})

    def _line(self, **values):
        defaults = {
            "name": "SpareBack Cable Kit",
            "partner_id": self.partner.id,
            "site_name": "SpareBack Site A",
            "sent_date": date(2026, 11, 2),
            "due_date": date(2026, 11, 9),
            "quantity_sent": 5.0,
            "quantity_consumed": 2.0,
        }
        defaults.update(values)
        return self.env["spare.return"].create(defaults)

    def test_01_line_defaults(self):
        line = self._line()
        self.assertEqual(line.state, "open")
        self.assertEqual(line.company_id, self.env.company)
        self.assertEqual(line.quantity_returned, 0.0)
        self.assertEqual(line.quantity_outstanding, 3.0)

    def test_02_register_return_closes_line(self):
        line = self._line(name="SpareBack Valve Kit")
        self.assertTrue(line.action_register_return())
        self.assertEqual(line.state, "returned")
        self.assertEqual(line.quantity_returned, 3.0)
        self.assertEqual(line.quantity_outstanding, 0.0)
        self.assertTrue(line.returned_on)

    def test_03_double_return_is_refused(self):
        line = self._line(name="SpareBack Sensor Kit")
        line.action_register_return()
        with self.assertRaises(ValidationError):
            line.action_register_return()

    def test_04_quantities_must_be_consistent(self):
        with self.assertRaises(ValidationError):
            self._line(name="SpareBack Zero Sent", quantity_sent=0.0)
        with self.assertRaises(ValidationError):
            self._line(name="SpareBack Negative Consumed",
                       quantity_consumed=-1.0)
        with self.assertRaises(ValidationError):
            self._line(name="SpareBack Too Much",
                       quantity_consumed=4.0, quantity_returned=2.0)

    def test_05_due_before_sent_is_refused(self):
        with self.assertRaises(ValidationError):
            self._line(name="SpareBack Bad Due",
                       sent_date=date(2026, 11, 10),
                       due_date=date(2026, 11, 5))

    def test_06_return_before_sent_is_refused(self):
        with self.assertRaises(ValidationError):
            self._line(name="SpareBack Bad Return",
                       returned_on=date(2026, 11, 1))

    def test_07_overdue_flag_and_filter(self):
        overdue = self._line(name="SpareBack Overdue",
                             sent_date=date(2026, 1, 1),
                             due_date=date(2026, 1, 5))
        future = self._line(name="SpareBack Future",
                            partner_id=self.partner_b.id,
                            due_date=date(2027, 1, 5))
        self.assertTrue(overdue.is_overdue)
        self.assertFalse(future.is_overdue)
        found = self.env["spare.return"].search([
            ("is_overdue", "=", True), ("state", "=", "open")])
        self.assertIn(overdue, found)
        self.assertNotIn(future, found)

    def test_08_company_isolation(self):
        foreign_partner = self.env["res.partner"].with_company(
            self.other_company).sudo().create({
                "name": "SpareBack Foreign Customer",
                "company_id": self.other_company.id,
            })
        foreign = self.env["spare.return"].with_company(
            self.other_company).sudo().create({
                "name": "SpareBack Foreign Line",
                "partner_id": foreign_partner.id,
                "sent_date": date(2026, 11, 12),
                "due_date": date(2026, 11, 19),
                "quantity_sent": 2.0,
                "company_id": self.other_company.id,
            })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._line(name="SpareBack Local Line")
        self.assertNotEqual(local.company_id, foreign.company_id)

    def test_09_outstanding_updates_when_consumed_changes(self):
        line = self._line(name="SpareBack Update Line", quantity_consumed=1.0)
        self.assertEqual(line.quantity_outstanding, 4.0)
        line.write({"quantity_consumed": 3.0})
        self.assertEqual(line.quantity_outstanding, 2.0)
