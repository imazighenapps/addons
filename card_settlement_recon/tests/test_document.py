# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestCardSettlement(TransactionCase):
    def test_flow(self):
        rec = self.env["card.settlement.recon"].create({
            "company_id": self.env.company.id, "provider": "Stripe", "gross_amount": 1000.0,
            "fees_amount": 25.0, "refunds_amount": 50.0, "transactions_count": 10})
        self.assertAlmostEqual(rec.net_amount, 925.0, places=2)
        rec.action_import(); rec.action_reconcile(); rec.action_post()
        self.assertEqual(rec.state, "posted")
        self.assertTrue(rec.export_file)
