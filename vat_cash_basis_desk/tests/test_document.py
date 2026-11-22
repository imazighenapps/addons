# -*- coding: utf-8 -*-
from datetime import date
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestVatCashBasis(TransactionCase):
    def test_compute(self):
        rec = self.env["vat.cash.basis.desk"].create({
            "company_id": self.env.company.id, "period_start": date(2025,1,1), "period_end": date(2025,1,31)})
        rec.action_compute()
        self.assertEqual(rec.state, "computed")
