# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# F1.2 -- best-effort mapping between the EduFlow payment method and the
# account.journal type used to record the matching accounting payment.
_METHOD_JOURNAL_TYPE = {
    'cash': 'cash',
    'transfer': 'bank',
    'cheque': 'bank',
    'card': 'bank',
    'online': 'bank',
}


class EduflowPayment(models.Model):
    _name = 'eduflow.payment'
    _description = "School Payment"
    _inherit = ['mail.thread']
    _order = 'date desc'

    name = fields.Char(string="Receipt No.", copy=False, readonly=True,
                        default=lambda self: 'New')
    fee_id = fields.Many2one('eduflow.fee', string="Due / Fee", required=True)
    student_id = fields.Many2one(related='fee_id.student_id', string="Student", store=True)
    date = fields.Date(string="Payment Date", default=fields.Date.context_today, required=True)
    amount = fields.Monetary(string="Amount", required=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='fee_id.currency_id', store=True)
    method = fields.Selection([
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
        ('cheque', 'Check'),
        ('card', 'Bank Card'),
        ('online', 'Online Payment'),
    ], string="Payment Method", required=True, default='cash')
    reference = fields.Char(string="Reference")
    account_payment_id = fields.Many2one('account.payment', string="Related Accounting Payment",
                                          help="Optional link to an Odoo account.payment.")
    company_id = fields.Many2one('res.company', string="Institution",
                                  related='fee_id.company_id', store=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='draft', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'eduflow.payment') or 'New'
        return super().create(vals_list)

    @api.constrains('amount', 'fee_id')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("Payment amount must be greater than zero.")

    def action_print_receipt(self):
        return self.env.ref('eduflow.action_report_eduflow_payment_receipt').report_action(self)

    def action_confirm(self):
        """Validate the payment: it only counts in paid_amount/remaining_amount
        (and therefore appears as paid on the parent portal) only once
        confirmed by the accountant, never upon simple entry.

        F1.2: when the related fee has already been invoiced (see
        eduflow.fee.action_create_invoice) and accounting synchronization is
        enabled, an account.payment is created/reconciled automatically so
        the cash actually collected is reflected in Accounting, not only in
        the EduFlow declarative tracking."""
        for rec in self:
            if rec.state != 'draft':
                continue
            rec.state = 'confirmed'
            if not self.env.context.get('eduflow_no_account_sync'):
                rec._sync_create_account_payment()

    def action_cancel(self):
        for rec in self:
            if not self.env.context.get('eduflow_no_account_sync'):
                rec._sync_cancel_account_payment()
        self.write({'state': 'cancelled'})

    def action_set_draft(self):
        self.write({'state': 'draft'})

    # ------------------------------------------------------------------
    # F1.2 -- accounting synchronization
    # ------------------------------------------------------------------
    def _eduflow_account_sync_enabled(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'eduflow.account_sync_enabled', 'True') == 'True'

    def _sync_create_account_payment(self):
        self.ensure_one()
        if self.account_payment_id or not self._eduflow_account_sync_enabled():
            return
        invoice = self.fee_id.invoice_id
        if not invoice or invoice.state == 'cancel':
            # F1.1 not activated for this fee: keep the current declarative
            # (degraded) behaviour, as required by the specification.
            return
        journal_type = _METHOD_JOURNAL_TYPE.get(self.method, 'bank')
        journal = self.env['account.journal'].search([
            ('type', '=', journal_type),
            ('company_id', '=', invoice.company_id.id),
        ], limit=1)
        if not journal:
            return
        AccountPayment = self.env['account.payment']
        account_payment = AccountPayment.create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': invoice.partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'journal_id': journal.id,
            'date': self.date,
            'ref': self.name,
        })
        account_payment.action_post()
        # Reconcile the payment with the invoice's open receivable line.
        payment_lines = account_payment.move_id.line_ids.filtered(
            lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled)
        invoice_lines = invoice.line_ids.filtered(
            lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled)
        (payment_lines + invoice_lines).reconcile()
        self.with_context(eduflow_no_account_sync=True).write({
            'account_payment_id': account_payment.id,
        })

    def _sync_cancel_account_payment(self):
        self.ensure_one()
        payment = self.account_payment_id
        if not payment:
            return
        if payment.state == 'posted':
            for line in payment.move_id.line_ids:
                if line.reconciled:
                    line.remove_move_reconcile()
            payment.action_cancel()
        self.with_context(eduflow_no_account_sync=True).write({'account_payment_id': False})
