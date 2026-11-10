# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCustomsDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "CustomsDesk Other Company"})
        cls.supplier = cls.env["res.partner"].create({
            "name": "CustomsDesk Supplier"})
        cls.country = cls.env.ref("base.cn")
        cls.code = cls.env["customs.duty.code"].create({
            "name": "Laptop computers",
            "code": "847130",
            "duty_rate": 5.0,
        })
        cls.entry = cls.env["customs.entry"].create({
            "name": "IMP-2026-001",
            "partner_id": cls.supplier.id,
            "country_id": cls.country.id,
            "declaration_date": date(2026, 11, 12),
        })

    def _line(self, entry=None, **values):
        defaults = {
            "entry_id": (entry or self.entry).id,
            "duty_code_id": self.code.id,
            "description": "CustomsDesk Test Laptop",
            "quantity": 10.0,
            "customs_value": 2000.0,
        }
        defaults.update(values)
        return self.env["customs.entry.line"].create(defaults)

    def test_01_defaults(self):
        self.assertEqual(self.entry.state, "draft")
        self.assertEqual(self.entry.company_id, self.env.company)
        self.assertEqual(self.entry.line_count, 0)
        self.assertAlmostEqual(self.code.duty_rate, 5.0, places=2)

    def test_02_line_duty_and_totals(self):
        line = self._line()
        self.assertAlmostEqual(line.duty_amount, 100.0, places=2)
        self._line(description="CustomsDesk Test Dock",
                   customs_value=500.0, quantity=5.0)
        self.entry.invalidate_recordset()
        self.assertEqual(self.entry.line_count, 2)
        self.assertAlmostEqual(self.entry.total_value, 2500.0, places=2)
        self.assertAlmostEqual(self.entry.total_duty, 125.0, places=2)

    def test_03_check_clear_workflow(self):
        self._line()
        self.assertTrue(self.entry.action_check())
        self.assertEqual(self.entry.state, "checked")
        self.assertTrue(self.entry.action_clear())
        self.assertEqual(self.entry.state, "cleared")
        self.assertTrue(self.entry.cleared_on)

    def test_04_reset_and_invalid_transitions(self):
        self._line()
        with self.assertRaises(UserError):
            self.entry.action_check() if False else self.entry.action_clear()
        self.entry.action_check()
        self.assertTrue(self.entry.action_reset())
        self.assertEqual(self.entry.state, "draft")
        with self.assertRaises(UserError):
            self.entry.action_reset()

    def test_05_cleared_entry_is_locked(self):
        self._line()
        self.entry.action_check()
        self.entry.action_clear()
        with self.assertRaises(UserError):
            self.entry.write({"name": "IMP-CHANGED"})
        with self.assertRaises(UserError):
            self._line(description="CustomsDesk Late Line")

    def test_06_line_value_constraints(self):
        with self.assertRaises(ValidationError):
            self._line(quantity=0)
        with self.assertRaises(ValidationError):
            self._line(customs_value=-1.0, description="CustomsDesk Negative")

    def test_07_hs_code_rate_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["customs.duty.code"].create({
                "name": "Bad rate",
                "code": "999999",
                "duty_rate": 120.0,
            })
        with self.assertRaises(ValidationError):
            self.env["customs.duty.code"].create({
                "name": "Negative rate",
                "code": "999998",
                "duty_rate": -1.0,
            })

    def test_08_company_isolation(self):
        foreign_partner = self.env["res.partner"].with_company(
            self.other_company).create({"name": "CustomsDesk Foreign Supplier"})
        foreign_country = self.env.ref("base.us")
        foreign_code = self.env["customs.duty.code"].with_company(
            self.other_company).create({
            "name": "Foreign code",
            "code": "850440",
            "duty_rate": 3.0,
            "company_id": self.other_company.id,
        })
        foreign = self.env["customs.entry"].with_company(
            self.other_company).create({
            "name": "IMP-FOREIGN-2026",
            "partner_id": foreign_partner.id,
            "country_id": foreign_country.id,
            "declaration_date": date(2026, 12, 5),
            "company_id": self.other_company.id,
        })
        self.env["customs.entry.line"].with_company(
            self.other_company).create({
            "entry_id": foreign.id,
            "duty_code_id": foreign_code.id,
            "description": "Foreign item",
            "quantity": 1.0,
            "customs_value": 1000.0,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(self.entry.company_id, self.env.company)
        self.assertAlmostEqual(foreign.total_duty, 30.0, places=2)
