# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVendorScore(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({
            "name": "Scored Supplier", "supplier_rank": 1})
        cls.product = cls.env["product.product"].create({
            "name": "Scored Component", "type": "consu",
            "is_storable": True, "standard_price": 10.0,
            "list_price": 20.0})

    def _review(self, quality=100.0):
        return self.env["vendor.review"].create({
            "partner_id": self.vendor.id,
            "period_start": date(2026, 1, 1),
            "period_end": date(2026, 12, 31),
            "quality_rate": quality,
        })

    def test_01_sequence_and_defaults(self):
        review = self._review()
        self.assertTrue(review.name.startswith("VSR/"))
        self.assertEqual(review.on_time_rate, 0.0)
        self.assertEqual(review.fill_rate, 0.0)

    def test_02_weighted_score(self):
        review = self._review()
        review.on_time_rate = 100.0
        review.fill_rate = 100.0
        review.price_variance = 0.0
        review.quality_rate = 100.0
        review._compute_score()
        self.assertAlmostEqual(review.score, 100.0, places=1)
        self.assertEqual(review.rating, "a")

    def test_03_low_score_is_d(self):
        review = self._review()
        review.on_time_rate = 20.0
        review.fill_rate = 20.0
        review.price_variance = 80.0
        review.quality_rate = 20.0
        review._compute_score()
        self.assertEqual(review.rating, "d")

    def test_04_compute_empty_period(self):
        review = self._review()
        review.action_compute()
        self.assertEqual(review.order_count, 0)
        self.assertAlmostEqual(review.on_time_rate, 100.0, places=1)
        self.assertAlmostEqual(review.fill_rate, 100.0, places=1)
        self.assertAlmostEqual(review.score, 100.0, places=1)

    def test_05_quality_constraint(self):
        with self.assertRaises(UserError):
            self._review(quality=130.0)

    def test_06_validate_d_requires_action(self):
        review = self._review()
        review.on_time_rate = 10.0
        review.fill_rate = 10.0
        review.quality_rate = 10.0
        review.price_variance = 90.0
        review._compute_score()
        self.assertEqual(review.rating, "d")
        with self.assertRaises(UserError):
            review.action_validate()
        self.env["vendor.action"].create({
            "review_id": review.id,
            "name": "Weekly delivery review",
            "deadline": date.today() + timedelta(days=7),
        })
        review.action_validate()
        self.assertEqual(review.state, "validated")
        self.assertTrue(review.validated_on)

    def test_07_partner_last_score(self):
        review = self._review()
        review.on_time_rate = 100.0
        review.fill_rate = 100.0
        review.quality_rate = 100.0
        review.price_variance = 0.0
        review._compute_score()
        self.vendor.invalidate_recordset()
        self.assertAlmostEqual(self.vendor.vendor_score, 100.0, places=1)
        self.assertEqual(self.vendor.vendor_rating, "a")
