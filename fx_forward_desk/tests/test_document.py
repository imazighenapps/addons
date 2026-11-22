# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestFxForward(TransactionCase):
    def test_flow(self):
        usd = self.env.ref("base.USD")
        rec = self.env["fx.forward.desk"].create({
            "company_id": self.env.company.id, "currency_id": usd.id,
            "counter_currency_id": self.env.company.currency_id.id,
            "amount": 10000.0, "forward_rate": 0.92, "maturity_date": date.today()+timedelta(days=30)})
        rec.action_open()
        self.assertEqual(rec.state, "open")
        rec.settlement_rate = 0.95
        rec.action_settle()
        self.assertAlmostEqual(rec.hedge_gain_loss, 300.0, places=2)
