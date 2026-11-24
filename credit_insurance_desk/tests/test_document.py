# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestCreditInsuranceCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Buyer"})

    def test_flow_and_limit(self):
        rec = self.env["credit.insurance.case"].create({
            "company_id": self.env.company.id, "insurer_name": "Euler", "partner_id": self.partner.id,
            "limit_amount": 1000.0, "monthly_sales": 1200.0})
        self.assertTrue(rec.over_limit)
        rec.action_declare()
        self.assertEqual(rec.state, "declared")
        self.assertAlmostEqual(rec.used_amount, 1200.0, places=2)
        rec.claim_amount = 500.0
        rec.action_claim()
        rec.indemnity_amount = 400.0
        rec.action_indemnify()
        self.assertEqual(rec.state, "indemnified")
