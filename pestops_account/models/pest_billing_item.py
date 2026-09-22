from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestBillingItem(models.Model):
    _name = 'pest.billing.item'
    _description = 'PestOps Billing Item'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'invoice_date desc, id desc'

    name = fields.Char(required=True, tracking=True)
    contract_id = fields.Many2one('pest.contract', required=True, ondelete='restrict', index=True)
    partner_id = fields.Many2one(related='contract_id.partner_id', store=True, index=True)
    company_id = fields.Many2one(related='contract_id.company_id', store=True, index=True)
    currency_id = fields.Many2one(related='contract_id.currency_id', store=True)

    source_type = fields.Selection([
        ('contract_period', 'Contract Period'),
        ('visit', 'Service Visit'),
        ('manual', 'Additional Service'),
    ], default='contract_period', required=True, tracking=True)
    visit_id = fields.Many2one('pest.visit', ondelete='restrict', index=True)

    period_start = fields.Date()
    period_end = fields.Date()
    invoice_date = fields.Date(default=fields.Date.context_today, required=True)

    product_id = fields.Many2one(
        'product.product',
        required=True,
        ondelete='restrict',
        domain="[('sale_ok', '=', True)]",
        help='Service product used on the customer invoice.',
    )
    description = fields.Text(required=True)
    quantity = fields.Float(default=1.0, required=True)
    unit_price = fields.Monetary(required=True, currency_field='currency_id')
    amount = fields.Monetary(compute='_compute_amount', store=True, currency_field='currency_id')

    state = fields.Selection([
        ('to_invoice', 'To Invoice'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled'),
    ], default='to_invoice', required=True, tracking=True)
    invoice_id = fields.Many2one('account.move', readonly=True, copy=False, index=True)

    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        for item in self:
            item.amount = item.quantity * item.unit_price

    @api.constrains('quantity', 'unit_price')
    def _check_amounts(self):
        for item in self:
            if item.quantity <= 0:
                raise ValidationError(_('Billing quantity must be greater than zero.'))
            if item.unit_price < 0:
                raise ValidationError(_('Billing unit price cannot be negative.'))

    @api.constrains('invoice_id', 'state')
    def _check_invoice_state(self):
        for item in self:
            if item.invoice_id and item.state != 'invoiced':
                raise ValidationError(_('An invoiced billing item must be in the Invoiced state.'))

    def action_cancel(self):
        for item in self.filtered(lambda r: r.state == 'to_invoice'):
            item.state = 'cancelled'

    def _generate_invoices(self):
        AccountMove = self.env['account.move']
        invoices = AccountMove
        groups = {}
        for item in self.filtered(lambda r: r.state == 'to_invoice' and not r.invoice_id):
            key = (item.company_id.id, item.partner_id.commercial_partner_id.id, item.currency_id.id, item.contract_id.billing_payment_term_id.id or False)
            groups.setdefault(key, self.env['pest.billing.item'])
            groups[key] |= item

        for _key, group in groups.items():
            first = group[0]
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': first.partner_id.commercial_partner_id.id,
                'company_id': first.company_id.id,
                'currency_id': first.currency_id.id,
                'invoice_date': max(group.mapped('invoice_date')),
                'payment_reference': first.contract_id.code if len(group.mapped('contract_id')) == 1 else _('PestOps Services'),
                'ref': ', '.join(group.mapped('contract_id.code'))[:200],
                'invoice_line_ids': [],
            }
            payment_term = first.contract_id.billing_payment_term_id
            if payment_term:
                invoice_vals['invoice_payment_term_id'] = payment_term.id

            line_commands = []
            for item in group.sorted(key=lambda r: (r.contract_id.id, r.invoice_date, r.id)):
                line_commands.append((0, 0, {
                    'product_id': item.product_id.id,
                    'name': item.description,
                    'quantity': item.quantity,
                    'price_unit': item.unit_price,
                }))
            invoice_vals['invoice_line_ids'] = line_commands
            invoice = AccountMove.create(invoice_vals)
            group.write({'invoice_id': invoice.id, 'state': 'invoiced'})
            invoices |= invoice
        return invoices

    def action_reset_to_invoice(self):
        for item in self.filtered(lambda r: r.state == 'cancelled'):
            if item.invoice_id:
                raise UserError(_('An item linked to an invoice cannot be reset.'))
            item.state = 'to_invoice'
