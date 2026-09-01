# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    """F1.2/F1.4 -- reverse synchronization: whenever an invoice generated
    from an eduflow.fee (see eduflow.fee.action_create_invoice) gets paid
    from the Accounting side -- including via the standard portal 'Pay Now'
    button once the 'payment' app is installed (F1.4) -- a matching,
    already-confirmed eduflow.payment is created/updated so the fee's
    state (paid/partial) and the parent portal reflect the real cash
    collected, without duplicating amounts already synced the other way
    round (see eduflow.payment._sync_create_account_payment)."""
    _inherit = 'account.move'

    def write(self, vals):
        res = super().write(vals)
        if 'payment_state' in vals and not self.env.context.get('eduflow_no_account_sync'):
            for move in self:
                if move.move_type == 'out_invoice':
                    move.sudo()._eduflow_sync_fee_payment()
        return res

    def _eduflow_sync_fee_payment(self):
        self.ensure_one()
        fee = self.env['eduflow.fee'].sudo().search([('invoice_id', '=', self.id)], limit=1)
        if not fee:
            return
        collected = self.amount_total - self.amount_residual
        already_synced = sum(fee.payment_ids.filtered(
            lambda p: p.state == 'confirmed' and p.account_payment_id).mapped('amount'))
        delta = collected - already_synced
        if delta <= 0.005:
            return
        payment = self.env['eduflow.payment'].sudo().with_context(
            eduflow_no_account_sync=True).create({
                'fee_id': fee.id,
                'amount': delta,
                'date': fields.Date.context_today(self),
                'method': 'online',
                'state': 'confirmed',
            })
        # Best-effort link to the accounting payment that triggered this
        # reconciliation, so a later cancellation can be un-reconciled too.
        account_payments = self.env['account.payment'].sudo().search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'posted'),
        ], order='id desc', limit=1)
        if account_payments:
            payment.account_payment_id = account_payments.id
