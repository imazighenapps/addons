# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFeedBridge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel = cls.env["feed.channel"].create({
            "name": "Test Google Feed",
            "backend": "google",
            "format": "xml",
            "base_url": "https://shop.example.com",
            "include_oos": True,
        })
        cls.good = cls.env["product.template"].create({
            "name": "Feed Valid Product",
            "default_code": "FEED-001",
            "list_price": 49.90,
            "description_sale": "A valid product for the feed.",
            "sale_ok": True,
        })
        cls.bad = cls.env["product.template"].create({
            "name": "Feed Invalid Product",
            "list_price": 0.0,
            "sale_ok": True,
        })

    def test_01_token(self):
        self.assertTrue(self.channel.token)
        self.assertGreater(len(self.channel.token), 10)

    def test_02_generate_xml(self):
        self.channel.action_generate()
        self.assertIn("Feed Valid Product", self.channel.content)
        self.assertIn("<g:price>49.90", self.channel.content)
        self.assertIn("https://shop.example.com/shop/", self.channel.content)
        self.assertTrue(self.channel.last_generation)
        self.assertTrue(self.channel.attachment_id)
        self.assertEqual(self.channel.mimetype, "application/xml")

    def test_03_validation_errors(self):
        self.channel.action_generate()
        errors = self.channel.log_ids.filtered(lambda l: l.level == "error")
        self.assertTrue(errors)
        self.assertIn("price", errors.mapped("field_name"))
        self.assertGreaterEqual(self.channel.error_count, 1)

    def test_04_csv_format(self):
        self.channel.format = "csv"
        self.channel.action_generate()
        self.assertTrue(
            self.channel.content.startswith("id,title,description"))
        self.assertIn("Feed Valid Product", self.channel.content)
        self.assertIn("FEED-001", self.channel.content)
        self.assertEqual(self.channel.mimetype, "text/csv")

    def test_05_meta_fields(self):
        self.channel.backend = "meta"
        self.channel.action_generate()
        self.assertNotIn("identifier_exists", self.channel.content)
        self.assertIn("image_link", self.channel.content)

    def test_06_min_price_filter(self):
        self.channel.min_price = 10.0
        self.channel.action_generate()
        self.assertNotIn("Feed Invalid Product", self.channel.content)
        self.assertGreaterEqual(self.channel.product_count, 1)

    def test_07_regeneration_replaces_logs(self):
        self.channel.action_generate()
        first = self.env["feed.log"].search_count(
            [("channel_id", "=", self.channel.id)])
        self.channel.action_generate()
        second = self.env["feed.log"].search_count(
            [("channel_id", "=", self.channel.id)])
        self.assertEqual(second, first)
        self.assertTrue(self.channel.attachment_id)
