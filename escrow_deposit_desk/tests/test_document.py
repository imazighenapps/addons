# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestEscrow(TransactionCase):
    def test_flow(self):
        rec = self.env["escrow.deposit.desk"].create({"company_id": self.env.company.id, "amount": 1000.0})
        rec.action_hold(); self.assertEqual(rec.state, "held")
        rec.action_release_all()
        self.assertEqual(rec.state, "released")
        self.assertAlmostEqual(rec.remaining_amount, 0.0, places=2)
