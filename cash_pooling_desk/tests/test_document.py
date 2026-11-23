# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError

@tagged("post_install", "-at_install")
class TestCashPoolingTransfer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.other = cls.env["res.company"].create({"name": "OtherCo"})

    def test_flow(self):
        rec = self.env["cash.pooling.transfer"].create({
            "company_id": self.company.id, "target_company_id": self.other.id,
            "amount": 12000.0, "interest_rate": 3.0, "direction": "to_pool"})
        self.assertAlmostEqual(rec.interest_amount, 30.0, places=2)
        rec.action_compute()
        self.assertEqual(rec.state, "computed")
        rec.action_post()
        self.assertEqual(rec.state, "posted")

    def test_same_company(self):
        with self.assertRaises(UserError):
            self.env["cash.pooling.transfer"].create({
                "company_id": self.company.id, "target_company_id": self.company.id, "amount": 100.0})
