# -*- coding: utf-8 -*-
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAssetPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["asset.category"].create({
            "name": "Test Machinery",
            "code": "TST-MACH",
            "method": "linear",
            "duration_months": 12,
            "declining_rate": 20.0,
        })
        cls.declining = cls.env["asset.category"].create({
            "name": "Test IT",
            "code": "TST-IT",
            "method": "declining",
            "duration_months": 24,
            "declining_rate": 50.0,
        })

    def _asset(self, **kwargs):
        values = {
            "name": "Test Forklift",
            "code": "TST-AST-01",
            "category_id": self.category.id,
            "acquisition_date": date.today() - relativedelta(years=1),
            "in_service_date": date.today() - relativedelta(years=1),
            "gross_value": 12000.0,
            "salvage_value": 0.0,
        }
        values.update(kwargs)
        return self.env["asset.record"].create(values)

    def test_01_create_defaults(self):
        asset = self._asset()
        self.assertEqual(asset.state, "draft")
        self.assertEqual(asset.method, "linear")
        self.assertEqual(asset.duration_months, 12)
        self.assertAlmostEqual(asset.residual_value, 12000.0, places=2)
        self.assertAlmostEqual(asset.remaining_depreciable, 12000.0, places=2)
        self.assertEqual(asset.line_count, 0)

    def test_02_validate_generates_schedule(self):
        asset = self._asset()
        asset.action_validate()
        self.assertEqual(asset.state, "running")
        self.assertEqual(asset.line_count, 12)
        self.assertAlmostEqual(
            sum(asset.depreciation_line_ids.mapped("amount")), 12000.0,
            places=2)

    def test_03_linear_schedule_with_salvage(self):
        asset = self._asset(gross_value=12000.0, salvage_value=1200.0)
        asset.action_validate()
        lines = asset.depreciation_line_ids
        self.assertEqual(len(lines), 12)
        for line in lines[:-1]:
            self.assertAlmostEqual(line.amount, 900.0, places=2)
        self.assertAlmostEqual(
            sum(lines.mapped("amount")), 10800.0, places=2)
        self.assertAlmostEqual(asset.residual_value, 12000.0, places=2)

    def test_04_declining_never_below_salvage(self):
        asset = self._asset(
            category_id=self.declining.id,
            acquisition_date=date.today() - relativedelta(years=3),
            in_service_date=date.today() - relativedelta(years=3),
            gross_value=10000.0, salvage_value=1000.0)
        asset.action_validate()
        lines = asset.depreciation_line_ids
        self.assertTrue(lines)
        self.assertAlmostEqual(
            sum(lines.mapped("amount")), 9000.0, places=2)
        for line in lines:
            self.assertGreater(line.amount, 0.0)
        asset.action_post_depreciation()
        self.assertGreaterEqual(asset.residual_value, 999.99)
        self.assertEqual(asset.state, "closed")

    def test_05_post_due_periods(self):
        asset = self._asset(
            acquisition_date=date.today() - relativedelta(months=6),
            in_service_date=date.today() - relativedelta(months=6))
        asset.action_validate()
        asset.action_post_depreciation()
        self.assertEqual(
            len(asset.depreciation_line_ids.filtered("posted")), 6)
        self.assertAlmostEqual(asset.posted_depreciation, 6000.0, places=2)
        self.assertAlmostEqual(asset.residual_value, 6000.0, places=2)
        self.assertEqual(asset.state, "running")

    def test_06_posting_all_closes_asset(self):
        asset = self._asset(
            acquisition_date=date.today() - relativedelta(years=1),
            in_service_date=date.today() - relativedelta(years=1))
        asset.action_validate()
        asset.action_post_depreciation()
        self.assertTrue(all(asset.depreciation_line_ids.mapped("posted")))
        self.assertAlmostEqual(asset.residual_value, 0.0, places=2)
        self.assertEqual(asset.state, "closed")

    def test_07_dispose_and_reset(self):
        asset = self._asset(
            acquisition_date=date.today() - relativedelta(months=6),
            in_service_date=date.today() - relativedelta(months=6))
        asset.action_validate()
        asset.action_post_depreciation()
        self.assertAlmostEqual(asset.residual_value, 6000.0, places=2)
        asset.write({
            "disposal_date": date.today(),
            "disposal_value": 7000.0,
        })
        asset.action_dispose()
        self.assertEqual(asset.state, "disposed")
        self.assertAlmostEqual(asset.disposal_gain_loss, 1000.0, places=2)
        asset.action_reset()
        self.assertEqual(asset.state, "running")
        self.assertFalse(asset.disposal_date)
        self.assertAlmostEqual(asset.disposal_gain_loss, 0.0, places=2)

    def test_08_constraints_and_errors(self):
        with self.assertRaises(ValidationError):
            self.env["asset.category"].create({
                "name": "Bad Duration", "duration_months": 0})
        with self.assertRaises(ValidationError):
            self.env["asset.category"].create({
                "name": "Bad Rate", "method": "declining",
                "duration_months": 12, "declining_rate": 0.0})
        with self.assertRaises(ValidationError):
            self._asset(gross_value=1000.0, salvage_value=2000.0)
        with self.assertRaises(ValidationError):
            self._asset(
                acquisition_date=date.today(),
                in_service_date=date.today() - relativedelta(days=10))
        asset = self._asset(gross_value=0.0)
        with self.assertRaises(UserError):
            asset.action_validate()
