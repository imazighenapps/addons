# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReportForge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Forge Customer", "city": "Lyon", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "Forge Product", "type": "service", "list_price": 150.0})
        cls.order = cls.env["sale.order"].create({
            "partner_id": cls.partner.id,
            "order_line": [(0, 0, {
                "product_id": cls.product.id, "product_uom_qty": 2,
                "price_unit": 150.0})],
        })

    def _template(self, body, model_name="res.partner"):
        return self.env["report.forge.template"].create({
            "name": "Test Template", "model_name": model_name,
            "body_html": body})

    def test_01_placeholder_render(self):
        template = self._template("<p>Dear {{ name }}, welcome to {{ city }}.</p>")
        document = self.env["report.forge.document"].create({
            "template_id": template.id,
            "res_model": "res.partner", "res_id": self.partner.id})
        document.action_generate()
        self.assertIn("Forge Customer", document.rendered_html)
        self.assertIn("Lyon", document.rendered_html)
        self.assertEqual(document.state, "done")
        self.assertTrue(document.attachment_id)

    def test_02_lines_table(self):
        template = self._template(
            "<p>{{ name }}</p>{{ lines }}", "sale.order")
        document = self.env["report.forge.document"].create({
            "template_id": template.id,
            "res_model": "sale.order", "res_id": self.order.id})
        document.action_generate()
        self.assertIn("Forge Product", document.rendered_html)
        self.assertIn("300.00", document.rendered_html)

    def test_03_unknown_field_is_empty(self):
        template = self._template("<p>{{ unknown_field }}</p>")
        header, body, _footer = template.render(self.partner)
        self.assertEqual(body.strip(), "<p></p>")

    def test_04_duplicate(self):
        template = self._template("<p>{{ name }}</p>")
        self.assertEqual(template.version, 1)
        action = template.action_duplicate()
        self.assertEqual(action["res_model"], "report.forge.template")

    def test_05_sequence(self):
        template = self._template("<p>{{ name }}</p>")
        document = self.env["report.forge.document"].create({
            "template_id": template.id,
            "res_model": "res.partner", "res_id": self.partner.id})
        self.assertTrue(document.name.startswith("DOC/"))
