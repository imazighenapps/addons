# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import EduflowTestCommon


@tagged('post_install', '-at_install')
class TestEduflowInvoicing(EduflowTestCommon):
    """F1.1 / F1.2 -- invoice generation from a fee and synchronization
    between eduflow.payment and account.payment."""

    def setUp(self):
        super().setUp()
        self.env['eduflow.student.parent.rel'].create({
            'student_id': self.student_1.id,
            'parent_id': self.parent_1.id,
            'relation': 'mother',
            'is_financial': True,
        })
        self.fee_type = self.env['eduflow.fee.type'].create({'name': 'Tuition Fee'})
        self.fee = self.env['eduflow.fee'].create({
            'student_id': self.student_1.id,
            'fee_type_id': self.fee_type.id,
            'year_id': self.year.id,
            'amount': 1000.0,
            'due_date': '2026-10-01',
        })

    def test_create_invoice_sets_state_and_partner(self):
        self.assertEqual(self.fee.invoice_state, 'not_invoiced')
        self.fee.action_create_invoice()
        self.assertEqual(self.fee.invoice_state, 'invoiced')
        self.assertTrue(self.fee.invoice_id)
        self.assertEqual(self.fee.invoice_id.move_type, 'out_invoice')
        self.assertEqual(self.fee.invoice_id.partner_id, self.parent_1_partner)

    def test_cannot_invoice_twice(self):
        self.fee.action_create_invoice()
        with self.assertRaises(UserError):
            self.fee.action_create_invoice()

    def test_cannot_invoice_without_financial_guardian(self):
        student_no_parent = self.env['eduflow.student'].create({
            'name': 'Sans', 'firstname': 'Parent', 'status': 'active',
        })
        fee_no_parent = self.env['eduflow.fee'].create({
            'student_id': student_no_parent.id,
            'fee_type_id': self.fee_type.id,
            'year_id': self.year.id,
            'amount': 500.0,
            'due_date': '2026-10-01',
        })
        # No eduflow.student.parent.rel at all for this student: there is no
        # contact to invoice, this must raise instead of silently failing.
        with self.assertRaises(UserError):
            fee_no_parent.action_create_invoice()

    def test_cancel_invoice_resets_state(self):
        self.fee.action_create_invoice()
        self.fee.action_cancel_invoice()
        self.assertEqual(self.fee.invoice_state, 'not_invoiced')
        self.assertFalse(self.fee.invoice_id)

    def test_payment_confirm_creates_account_payment(self):
        """F1.2: confirming a payment on an invoiced fee must create and
        reconcile a matching account.payment."""
        self.fee.action_create_invoice()
        payment = self.env['eduflow.payment'].create({
            'fee_id': self.fee.id, 'amount': 1000.0, 'method': 'transfer',
        })
        payment.action_confirm()
        self.assertTrue(payment.account_payment_id)
        self.assertEqual(payment.account_payment_id.state, 'posted')
        self.assertEqual(self.fee.invoice_id.payment_state, 'paid')

    def test_payment_confirm_without_invoice_stays_declarative(self):
        """When the fee has not been invoiced, EduFlow keeps its previous
        (degraded) behaviour: no account.payment is created."""
        payment = self.env['eduflow.payment'].create({
            'fee_id': self.fee.id, 'amount': 1000.0, 'method': 'cash',
        })
        payment.action_confirm()
        self.assertFalse(payment.account_payment_id)
        self.assertEqual(self.fee.state, 'paid')

    def test_cancel_payment_cancels_account_payment(self):
        self.fee.action_create_invoice()
        payment = self.env['eduflow.payment'].create({
            'fee_id': self.fee.id, 'amount': 1000.0, 'method': 'cash',
        })
        payment.action_confirm()
        account_payment = payment.account_payment_id
        payment.action_cancel()
        self.assertFalse(payment.account_payment_id)
        self.assertEqual(account_payment.state, 'cancel')
