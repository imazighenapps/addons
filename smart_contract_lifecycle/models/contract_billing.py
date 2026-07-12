from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ContractBillingLine(models.Model):
    _name = 'contract.billing.line'
    _description = 'Recurring Billing Line'
    _order = 'sequence, id'

    contract_id = fields.Many2one(
        'contract.contract', string='Contract',
        required=True, ondelete='cascade',
    )
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one(
        'product.product', string='Product / Service',
        required=True,
    )
    name = fields.Char(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price', required=True)
    currency_id = fields.Many2one(
        related='contract_id.currency_id', store=True, readonly=True,
    )
    subtotal = fields.Monetary(
        string='Subtotal', compute='_compute_subtotal',
        currency_field='currency_id', store=True,
    )

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.price_unit = self.product_id.list_price


class ContractContractBilling(models.Model):
    _inherit = 'contract.contract'

    billing_line_ids = fields.One2many(
        'contract.billing.line', 'contract_id', string='Billing Lines',
    )
    auto_invoice = fields.Boolean(
        string='Automatic Billing', default=False, tracking=True,
        help="Automatically generates invoices according to the configured frequency.",
    )
    next_invoice_date = fields.Date(
        string='Next Invoice Date', tracking=True, copy=False,
    )
    invoice_ids = fields.One2many(
        'account.move', 'contract_id', string='Generated Invoices',
    )
    invoice_count = fields.Integer(
        string='Invoice Count', compute='_compute_invoice_count',
    )

    _FREQUENCY_DELTA = {
        'monthly': relativedelta(months=1),
        'quarterly': relativedelta(months=3),
        'semi_annual': relativedelta(months=6),
        'annual': relativedelta(years=1),
    }

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)

    @api.onchange('billing_frequency', 'date_start', 'auto_invoice')
    def _onchange_billing_frequency(self):
        if self.auto_invoice and self.billing_frequency != 'one_time' and self.date_start:
            if not self.next_invoice_date:
                self.next_invoice_date = self.date_start
        elif self.billing_frequency == 'one_time':
            self.auto_invoice = False
            self.next_invoice_date = False

    @api.constrains('auto_invoice', 'billing_frequency', 'billing_line_ids')
    def _check_auto_invoice(self):
        for rec in self:
            if rec.auto_invoice:
                if rec.billing_frequency == 'one_time':
                    raise UserError(_(
                        "Automatic billing requires a recurring frequency "
                        "(monthly, quarterly, etc.)."
                    ))
                if not rec.billing_line_ids:
                    raise UserError(_(
                        "Add at least one billing line before enabling "
                        "automatic billing."
                    ))

    def action_generate_invoice_now(self):
        """Generates an invoice immediately."""
        self.ensure_one()
        if not self.billing_line_ids:
            raise UserError(_("No billing line defined on this contract."))
        move = self._create_recurring_invoice()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Invoice'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': move.id,
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices — %s') % self.name,
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
        }

    def _create_recurring_invoice(self):
        """Creates an account.move (customer or vendor invoice) from
        the contract's billing lines."""
        self.ensure_one()
        move_type = 'out_invoice' if self.contract_type in (
            'customer', 'service', 'partnership', 'other',
        ) else 'in_invoice'

        invoice_lines = []
        for line in self.billing_line_ids:
            invoice_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
            }))

        move = self.env['account.move'].create({
            'move_type': move_type,
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'invoice_origin': self.name,
            'contract_id': self.id,
            'invoice_payment_term_id': self.payment_terms_id.id or False,
            'invoice_line_ids': invoice_lines,
        })
        self.message_post(
            body=_('Invoice %s generated automatically (%s).') % (
                move.name or _('Draft'), dict(self._fields['billing_frequency'].selection).get(self.billing_frequency),
            ),
            message_type='comment', subtype_xmlid='mail.mt_note',
        )
        return move

    @api.model
    def _cron_generate_recurring_invoices(self):
        """Generates the invoices due for all active contracts with
        automatic billing whose next due date has been reached."""
        today = fields.Date.today()
        contracts = self.sudo().search([
            ('state', '=', 'active'),
            ('auto_invoice', '=', True),
            ('next_invoice_date', '<=', today),
            ('billing_frequency', '!=', 'one_time'),
        ])
        for contract in contracts:
            try:
                contract._create_recurring_invoice()
                delta = contract._FREQUENCY_DELTA.get(
                    contract.billing_frequency, relativedelta(months=1),
                )
                contract.next_invoice_date = contract.next_invoice_date + delta
            except Exception as exc:  # noqa: BLE001
                contract.message_post(
                    body=_('Automatic invoice generation failed: %s') % exc,
                    message_type='comment', subtype_xmlid='mail.mt_note',
                )
