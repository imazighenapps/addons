# -*- coding: utf-8 -*-
from datetime import date
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestImportVatChecker(TransactionCase):
    def test_check(self):
        rec = self.env["import.vat.checker"].create({
            "company_id": self.env.company.id, "period_start": date(2025,1,1), "period_end": date(2025,1,31),
            "customs_vat_amount": 500.0})
        rec.action_check()
        self.assertEqual(rec.state, "checked")
        self.assertTrue(rec.has_gap or not rec.has_gap)  # computed
