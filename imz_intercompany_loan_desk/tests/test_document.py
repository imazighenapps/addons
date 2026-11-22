# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestIntercompanyLoan(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.other = cls.env["res.company"].create({"name": "BorrowerCo"})

    def test_flow(self):
        rec = self.env["intercompany.loan"].create({
            "company_id": self.company.id, "borrower_company_id": self.other.id,
            "principal_amount": 12000.0, "interest_rate": 4.0, "term_months": 12})
        self.assertAlmostEqual(rec.monthly_payment, 1000.0, places=2)
        self.assertTrue(rec.maturity_date)
        rec.action_start()
        self.assertEqual(rec.state, "running")
        rec.action_close()
        self.assertEqual(rec.state, "closed")
