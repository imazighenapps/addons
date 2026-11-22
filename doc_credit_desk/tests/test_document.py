# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestDocCredit(TransactionCase):
    def test_flow(self):
        rec = self.env["doc.credit.desk"].create({
            "company_id": self.env.company.id, "amount": 5000.0, "lc_type": "import"})
        rec.action_open(); self.assertEqual(rec.state, "open")
        rec.action_present(); rec.action_accept(); rec.action_settle()
        self.assertEqual(rec.state, "settled")
