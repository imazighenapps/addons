# -*- coding: utf-8 -*-
from odoo.tests import tagged

from .common import EduflowTestCommon


@tagged('post_install', '-at_install')
class TestEduflowPayment(EduflowTestCommon):

    def setUp(self):
        super().setUp()
        self.fee_type = self.env['eduflow.fee.type'].create({'name': 'Tuition Fee'})
        self.fee = self.env['eduflow.fee'].create({
            'student_id': self.student_1.id,
            'fee_type_id': self.fee_type.id,
            'year_id': self.year.id,
            'amount': 1000.0,
            'due_date': '2026-10-01',
        })

    def test_payment_defaults_to_draft(self):
        """Regression: a newly entered payment must not count
        as paid until it has been explicitly confirmed."""
        payment = self.env['eduflow.payment'].create({
            'fee_id': self.fee.id, 'amount': 400.0, 'method': 'cash',
        })
        self.assertEqual(payment.state, 'draft')
        self.assertEqual(self.fee.paid_amount, 0.0,
                          "A draft payment must not be counted in paid_amount")
        self.assertEqual(self.fee.state, 'pending')

        payment.action_confirm()
        self.assertEqual(self.fee.paid_amount, 400.0)
        self.assertEqual(self.fee.state, 'partial')

    def test_cancelled_payment_not_counted(self):
        payment = self.env['eduflow.payment'].create({
            'fee_id': self.fee.id, 'amount': 1000.0, 'method': 'transfer',
        })
        payment.action_confirm()
        self.assertEqual(self.fee.state, 'paid')
        payment.action_cancel()
        self.assertEqual(self.fee.paid_amount, 0.0)
        self.assertEqual(self.fee.state, 'pending')
