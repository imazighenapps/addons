# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestMarketplaceSettlement(TransactionCase):
    def test_flow(self):
        rec = self.env["marketplace.settlement.recon"].create({
            "company_id": self.env.company.id, "marketplace": "Amazon", "sales_amount": 2000.0,
            "commissions_amount": 300.0, "ads_amount": 100.0, "refunds_amount": 50.0})
        self.assertAlmostEqual(rec.net_amount, 1550.0, places=2)
        rec.action_import(); rec.action_reconcile(); rec.action_post()
        self.assertEqual(rec.state, "posted")
