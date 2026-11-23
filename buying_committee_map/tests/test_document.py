# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import tagged

@tagged("post_install", "-at_install")
class TestBuyingCommitteeMap(TransactionCase):
    def test_flow(self):
        rec = self.env["buying.committee.map"].create({
            "description": "Test",
            "amount": 10.0,
        })
        self.assertEqual(rec.state, "draft")
        rec.action_confirm()
        self.assertNotEqual(rec.name, "Nouveau")
        self.assertEqual(rec.state, "confirmed")
        rec.action_start()
        self.assertEqual(rec.state, "in_progress")
        rec.action_export()
        self.assertTrue(rec.export_file)
        rec.action_done()
        self.assertEqual(rec.state, "done")
