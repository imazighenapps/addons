# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBackorderDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "BackorderDesk Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "BackorderDesk Test Customer"})
        cls.case = cls.env["backorder.case"].create({
            "name": "BackorderDesk Case A",
            "partner_id": cls.partner.id,
            "product_name": "BackorderDesk Test Widget",
            "ordered_qty": 10.0,
            "missing_qty": 4.0,
            "promised_date": date(2026, 12, 15),
            "customer_message": "We expect to ship the remainder soon.",
        })

    def _update(self, **values):
        defaults = {
            "name": "BackorderDesk Update",
            "case_id": self.case.id,
            "update_date": date(2026, 11, 2),
            "message": "Customer informed about the delay.",
        }
        defaults.update(values)
        return self.env["backorder.update"].create(defaults)

    def test_01_case_defaults(self):
        self.assertEqual(self.case.state, "open")
        self.assertEqual(self.case.company_id, self.env.company)
        self.assertEqual(self.case.update_count, 0)
        self.assertFalse(self.case.is_late)

    def test_02_update_count(self):
        self._update()
        self._update(name="BackorderDesk Update 2",
                     update_date=date(2026, 11, 3))
        self.case.invalidate_recordset()
        self.assertEqual(self.case.update_count, 2)

    def test_03_resolve_and_reopen(self):
        self.assertTrue(self.case.action_resolve())
        self.assertEqual(self.case.state, "resolved")
        self.assertTrue(self.case.resolved_on)
        self.assertTrue(self.case.action_reopen())
        self.assertEqual(self.case.state, "open")
        self.assertFalse(self.case.resolved_on)

    def test_04_double_resolve_refused(self):
        self.case.action_resolve()
        with self.assertRaises(ValidationError):
            self.case.action_resolve()

    def test_05_quantity_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["backorder.case"].create({
                "name": "BackorderDesk Bad Ordered",
                "partner_id": self.partner.id,
                "product_name": "BackorderDesk Item",
                "ordered_qty": 0.0,
                "missing_qty": 1.0,
                "promised_date": date(2026, 12, 1),
            })
        with self.assertRaises(ValidationError):
            self.case.write({"missing_qty": 20.0})

    def test_06_late_flag_for_past_promise(self):
        late = self.env["backorder.case"].create({
            "name": "BackorderDesk Late Case",
            "partner_id": self.partner.id,
            "product_name": "BackorderDesk Late Item",
            "ordered_qty": 5.0,
            "missing_qty": 2.0,
            "promised_date": fields.Date.today() - timedelta(days=2),
        })
        self.assertTrue(late.is_late)
        late.action_resolve()
        late.invalidate_recordset()
        self.assertFalse(late.is_late)

    def test_07_update_dates_constraint(self):
        with self.assertRaises(ValidationError):
            self._update(update_date=date(2026, 11, 5),
                         new_promised_date=date(2026, 11, 1))

    def test_08_company_isolation(self):
        foreign_partner = self.env["res.partner"].sudo().create({
            "name": "BackorderDesk Foreign Customer"})
        foreign = self.env["backorder.case"].with_company(
            self.other_company).sudo().create({
            "name": "BackorderDesk Foreign Case",
            "partner_id": foreign_partner.id,
            "product_name": "BackorderDesk Foreign Item",
            "ordered_qty": 3.0,
            "missing_qty": 1.0,
            "promised_date": date(2026, 12, 20),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(self.case.company_id, self.env.company)

from odoo import fields  # noqa: E402
