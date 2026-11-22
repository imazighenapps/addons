# -*- coding: utf-8 -*-
from datetime import date
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTnFiscalDeclaration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

    def test_generate_and_flow(self):
        vals = {"company_id": self.company.id, "period_start": date(2025,1,1), "period_end": date(2025,1,31)}
        doc = self.env["tn.fiscal.declaration"].create(vals)
        doc.action_generate()
        self.assertEqual(doc.state, "ready")
        self.assertTrue(doc.file_data)
        self.assertTrue(doc.file_name)
        doc.action_mark_sent()
        self.assertEqual(doc.state, "sent")
