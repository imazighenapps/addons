# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIntrastat(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country = cls.env.ref("base.be")
        cls.other_company = cls.env["res.company"].create({
            "name": "Intrastat Other Company"})
        cls.report = cls.env["intra.report"].create({
            "name": "Intrastat 2026-11 Dispatch",
            "direction": "dispatch",
            "period_start": date(2026, 11, 1),
            "period_end": date(2026, 11, 30),
        })

    def _line(self, report=None, **values):
        defaults = {
            "report_id": (report or self.report).id,
            "partner_country_id": self.country.id,
            "commodity_code": "84713000",
            "product_name": "Intrastat Test Laptop",
            "quantity": 2.0,
            "value": 1200.0,
            "weight": 4.5,
        }
        defaults.update(values)
        return self.env["intra.flow"].create(defaults)

    def test_01_report_defaults(self):
        self.assertEqual(self.report.state, "draft")
        self.assertEqual(self.report.direction, "dispatch")
        self.assertEqual(self.report.company_id, self.env.company)
        self.assertEqual(self.report.line_count, 0)
        self.assertFalse(self.report.filed_on)

    def test_02_flow_line_updates_totals(self):
        self._line(value=1200.0, weight=4.5)
        self._line(product_name="Intrastat Test Screen",
                   commodity_code="85285210", value=300.0, weight=3.0)
        self.report.invalidate_recordset()
        self.assertEqual(self.report.line_count, 2)
        self.assertAlmostEqual(self.report.total_value, 1500.0, places=2)
        self.assertAlmostEqual(self.report.total_weight, 7.5, places=2)

    def test_03_review_file_workflow(self):
        self._line()
        self.assertTrue(self.report.action_review())
        self.assertEqual(self.report.state, "review")
        self.assertTrue(self.report.action_file())
        self.assertEqual(self.report.state, "filed")
        self.assertTrue(self.report.filed_on)

    def test_04_reset_from_review(self):
        self._line()
        self.report.action_review()
        self.assertTrue(self.report.action_reset())
        self.assertEqual(self.report.state, "draft")
        with self.assertRaises(UserError):
            self.report.action_reset()

    def test_05_review_requires_lines_and_file_requires_review(self):
        with self.assertRaises(UserError):
            self.report.action_review()
        self._line()
        with self.assertRaises(UserError):
            self.report.action_file()
        self.report.action_review()
        with self.assertRaises(UserError):
            self.report.action_review()

    def test_06_filed_report_is_locked(self):
        self._line()
        self.report.action_review()
        self.report.action_file()
        with self.assertRaises(UserError):
            self.report.write({"name": "Intrastat Changed"})
        with self.assertRaises(UserError):
            self._line(product_name="Intrastat Late Line")

    def test_07_period_and_line_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["intra.report"].create({
                "name": "Intrastat Bad Period",
                "direction": "arrival",
                "period_start": date(2026, 11, 30),
                "period_end": date(2026, 11, 1),
            })
        with self.assertRaises(ValidationError):
            self._line(quantity=0)
        with self.assertRaises(ValidationError):
            self._line(value=-10.0, product_name="Intrastat Negative Value")
        with self.assertRaises(ValidationError):
            self._line(weight=0, product_name="Intrastat Zero Weight")

    def test_08_company_isolation(self):
        foreign_country = self.env.ref("base.de")
        foreign = self.env["intra.report"].with_company(
            self.other_company).create({
            "name": "Intrastat Foreign 2026-12",
            "direction": "arrival",
            "period_start": date(2026, 12, 1),
            "period_end": date(2026, 12, 31),
            "company_id": self.other_company.id,
        })
        self.env["intra.flow"].with_company(self.other_company).create({
            "report_id": foreign.id,
            "partner_country_id": foreign_country.id,
            "commodity_code": "30049000",
            "product_name": "Intrastat Foreign Goods",
            "quantity": 1.0,
            "value": 500.0,
            "weight": 1.0,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(self.report.company_id, self.env.company)
        self.assertEqual(foreign.line_count, 1)
