# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductQuality(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_barcode = cls.env["product.quality.rule"].create({
            "name": "ProductQuality Barcode Required",
            "field_key": "barcode",
            "severity": "error",
            "points": 10,
        })
        cls.rule_cost = cls.env["product.quality.rule"].create({
            "name": "ProductQuality Cost Required",
            "field_key": "cost",
            "points": 5,
        })
        cls.rule_weight = cls.env["product.quality.rule"].create({
            "name": "ProductQuality Weight Required",
            "field_key": "weight",
            "points": 5,
        })
        cls.rule_price = cls.env["product.quality.rule"].create({
            "name": "ProductQuality Sale Price Required",
            "field_key": "sale_price",
            "points": 5,
        })

    def _product(self, **values):
        """A product of the current company, created for this test only."""
        name = values.pop("name", "ProductQuality Test Product")
        product = self.env["product.product"].create({"name": name})
        if values:
            product.write(values)
        return product

    def _scan(self, rules, products=None):
        values = {
            "name": "ProductQuality Test Scan",
            "rule_ids": [(6, 0, rules.ids)],
        }
        if products:
            values["product_ids"] = [(6, 0, products.ids)]
        scan = self.env["product.quality.scan"].create(values)
        self.env.flush_all()
        scan.action_run()
        scan.invalidate_recordset()
        return scan

    def test_01_missing_barcode_creates_one_anomaly(self):
        product = self._product()
        self.assertFalse(product.barcode)
        scan = self._scan(self.rule_barcode, product)
        lines = scan.line_ids.filtered(
            lambda line: line.product_id == product)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines.field_key, "barcode")
        self.assertEqual(lines.severity, "error")
        self.assertEqual(lines.state, "new")
        self.assertIn("barcode", lines.message)
        self.assertEqual(scan.anomaly_count, 1)
        self.assertEqual(scan.product_count, 1)
        self.assertEqual(scan.score, 0.0)

    def test_02_complete_product_scores_one_hundred(self):
        product = self._product(
            barcode="PQTESTCPLETE",
            standard_price=12.0,
            list_price=25.0,
            weight=1.5,
            description_sale="A complete product sheet.",
        )
        rules = (self.rule_barcode | self.rule_cost
                 | self.rule_weight | self.rule_price)
        scan = self._scan(rules, product)
        self.assertFalse(scan.line_ids)
        self.assertEqual(scan.anomaly_count, 0)
        self.assertEqual(scan.product_count, 1)
        self.assertEqual(scan.score, 100.0)

    def test_03_score_is_weighted_by_rule_points(self):
        rules = self.rule_barcode | self.rule_cost
        # Barcode set, cost still at zero: 5 missing points out of 15.
        product = self._product(barcode="PQTESTWEIGHT")
        scan = self._scan(rules, product)
        self.assertEqual(scan.anomaly_count, 1)
        self.assertAlmostEqual(scan.score, 66.67, places=2)
        # Nothing set: the whole 15 points are missing.
        empty = self._product()
        empty_scan = self._scan(rules, empty)
        self.assertEqual(empty_scan.anomaly_count, 2)
        self.assertEqual(empty_scan.score, 0.0)

    def test_04_second_run_is_idempotent(self):
        product = self._product()
        scan = self._scan(self.rule_barcode | self.rule_cost, product)
        self.assertEqual(len(scan.line_ids), 2)
        score = scan.score
        scan.action_run()
        scan.invalidate_recordset()
        self.assertEqual(len(scan.line_ids), 2)
        self.assertEqual(scan.anomaly_count, 2)
        self.assertEqual(scan.score, score)

    def test_05_mark_fixed_and_ignore(self):
        product = self._product()
        scan = self._scan(self.rule_barcode | self.rule_cost, product)
        line = scan.line_ids.filtered(
            lambda item: item.field_key == "barcode")
        other = scan.line_ids - line
        self.assertTrue(line.action_mark_fixed())
        self.assertEqual(line.state, "fixed")
        self.assertEqual(other.state, "new")
        self.assertTrue(other.action_ignore())
        self.assertEqual(other.state, "ignored")

    def test_06_run_and_reset_states(self):
        product = self._product()
        scan = self.env["product.quality.scan"].create({
            "name": "ProductQuality Test Reset",
            "rule_ids": [(6, 0, self.rule_barcode.ids)],
            "product_ids": [(6, 0, product.ids)],
        })
        self.assertEqual(scan.state, "draft")
        self.assertEqual(scan.score, 100.0)
        scan.action_run()
        scan.invalidate_recordset()
        self.assertEqual(scan.state, "done")
        self.assertTrue(scan.line_ids)
        self.assertEqual(scan.product_count, 1)
        self.assertTrue(scan.action_reset())
        scan.invalidate_recordset()
        self.assertEqual(scan.state, "draft")
        self.assertFalse(scan.line_ids)
        self.assertEqual(scan.anomaly_count, 0)
        self.assertEqual(scan.score, 100.0)

    def test_07_rule_is_unique_per_company_and_field(self):
        with self.assertRaises(ValidationError):
            self.env["product.quality.rule"].create({
                "name": "ProductQuality Negative Points",
                "field_key": "description",
                "points": -3,
            })
        # The SQL uniqueness error surfaces as a wrapped ValidationError on
        # some series and as a raw IntegrityError on others (19.0), and
        # assertRaises does not take a tuple there: catch both manually
        # inside a savepoint so the transaction stays usable.
        before = self.env["product.quality.rule"].search_count([])
        raised = False
        try:
            with self.env.cr.savepoint():
                self.env["product.quality.rule"].create({
                    "name": "ProductQuality Barcode Again",
                    "field_key": "barcode",
                    "points": 3,
                })
                self.env.flush_all()
        except (ValidationError, IntegrityError):
            raised = True
        self.assertTrue(raised)
        self.assertEqual(
            self.env["product.quality.rule"].search_count([]), before)

    def test_08_other_company_products_are_not_scanned(self):
        other_company = self.env["res.company"].create({
            "name": "ProductQuality Other Company",
        })
        template = self.env["product.template"].create({
            "name": "ProductQuality Foreign Product",
            "company_id": other_company.id,
        })
        foreign = template.product_variant_id
        product = self._product()
        scan = self._scan(self.rule_barcode)
        self.assertEqual(scan.company_id, self.env.company)
        self.assertNotIn(foreign, scan.scanned_product_ids)
        self.assertIn(product, scan.scanned_product_ids)
        self.assertFalse(scan.line_ids.filtered(
            lambda line: line.product_id == foreign))
        for line in scan.line_ids:
            self.assertIn(line.company_id, self.env.company)
