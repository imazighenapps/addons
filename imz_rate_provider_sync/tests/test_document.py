# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestRateProviderSync(TransactionCase):
    def test_sync(self):
        usd = self.env.ref("base.USD")
        rec = self.env["rate.provider.sync"].create({
            "company_id": self.env.company.id, "currency_id": usd.id, "rate": 1.1, "previous_rate": 1.0, "alert_threshold": 5.0})
        self.assertTrue(rec.alert)
        rec.action_sync()
        self.assertEqual(rec.state, "synced")
