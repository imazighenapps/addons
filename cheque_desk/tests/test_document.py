# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestChequeRegister(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Client CHQ"})

    def test_flow(self):
        rec = self.env["cheque.register"].create({
            "company_id": self.env.company.id, "partner_id": self.partner.id,
            "cheque_number": "CHQ-001", "amount": 1200.0, "bank_name": "BNP"})
        rec.action_deposit()
        self.assertEqual(rec.state, "deposited")
        rec.action_clear()
        self.assertEqual(rec.state, "cleared")
        self.assertTrue(rec.clearing_date)

    def test_reject(self):
        rec = self.env["cheque.register"].create({
            "company_id": self.env.company.id, "partner_id": self.partner.id,
            "cheque_number": "CHQ-002", "amount": 300.0})
        rec.action_deposit()
        rec.action_reject()
        self.assertEqual(rec.state, "rejected")
        self.assertEqual(rec.incident_count, 1)
