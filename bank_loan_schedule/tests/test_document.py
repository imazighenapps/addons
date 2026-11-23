# -*- coding: utf-8 -*-
from datetime import date
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestBankLoan(TransactionCase):
    def test_schedule_and_pay(self):
        loan = self.env["bank.loan"].create({
            "company_id": self.env.company.id, "principal_amount": 12000.0, "interest_rate": 3.6,
            "insurance_rate": 0.24, "term_months": 12, "start_date": date(2025,1,1)})
        loan.action_generate_schedule()
        self.assertEqual(loan.state, "running")
        self.assertEqual(len(loan.line_ids), 12)
        self.assertAlmostEqual(sum(loan.line_ids.mapped("capital_amount")), 12000.0, places=2)
        loan.action_mark_paid_next()
        self.assertEqual(loan.line_ids.sorted('sequence')[0].state, "paid")
