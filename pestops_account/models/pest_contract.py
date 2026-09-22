from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PestContract(models.Model):
    _inherit = 'pest.contract'

    billing_product_id = fields.Many2one(
        'product.product',
        string='Billing Service Product',
        domain="[('sale_ok', '=', True)]",
        help='Default service product used to invoice the recurring contract.',
    )
    billing_payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Invoice Payment Terms',
    )
    billing_item_ids = fields.One2many(
        'pest.billing.item', 'contract_id',
        string='Billing Items',
        readonly=True,
    )
    billing_item_count = fields.Integer(compute='_compute_billing_kpis')
    billing_invoice_count = fields.Integer(compute='_compute_billing_kpis')
    billing_to_invoice_amount = fields.Monetary(compute='_compute_billing_kpis', currency_field='currency_id')
    billing_invoiced_amount = fields.Monetary(compute='_compute_billing_kpis', currency_field='currency_id')

    @api.depends('billing_item_ids.state', 'billing_item_ids.amount', 'billing_item_ids.invoice_id')
    def _compute_billing_kpis(self):
        for contract in self:
            items = contract.billing_item_ids
            contract.billing_item_count = len(items)
            contract.billing_invoice_count = len(items.mapped('invoice_id'))
            contract.billing_to_invoice_amount = sum(items.filtered(lambda x: x.state == 'to_invoice').mapped('amount'))
            contract.billing_invoiced_amount = sum(items.filtered(lambda x: x.state == 'invoiced').mapped('amount'))

    def _billing_period_step(self):
        self.ensure_one()
        return {
            'monthly': relativedelta(months=1),
            'quarterly': relativedelta(months=3),
            'annual': relativedelta(years=1),
        }.get(self.billing_frequency)

    def _billing_period_end(self, start):
        self.ensure_one()
        step = self._billing_period_step()
        if not step:
            return start
        return start + step - timedelta(days=1)

    def _billing_horizon_end(self):
        self.ensure_one()
        if self.end_date:
            return self.end_date
        today = fields.Date.context_today(self)
        step = self._billing_period_step() or relativedelta(months=1)
        return max(today, self.start_date) + step * 11

    def action_prepare_billing(self):
        BillingItem = self.env['pest.billing.item']
        today = fields.Date.context_today(self)
        for contract in self:
            if contract.state not in ('confirmed', 'to_renew'):
                raise UserError(_('Only confirmed or to-renew contracts can be prepared for billing.'))
            if not contract.billing_product_id:
                raise UserError(_('Set a Billing Service Product on contract %s first.') % contract.display_name)
            if not contract.partner_id:
                raise UserError(_('A customer is required before billing.'))

            if contract.billing_frequency == 'per_visit':
                done_visits = contract.visit_ids.filtered(lambda v: v.state == 'done')
                existing_visit_ids = set(contract.billing_item_ids.filtered(lambda i: i.source_type == 'visit' and i.visit_id).mapped('visit_id').ids)
                for visit in done_visits:
                    if visit.id in existing_visit_ids:
                        continue
                    BillingItem.create({
                        'name': _('Visit %s') % visit.name,
                        'contract_id': contract.id,
                        'source_type': 'visit',
                        'visit_id': visit.id,
                        'period_start': visit.actual_start.date() if visit.actual_start else today,
                        'period_end': visit.actual_end.date() if visit.actual_end else (visit.actual_start.date() if visit.actual_start else today),
                        'invoice_date': (visit.actual_end or visit.actual_start or fields.Datetime.now()).date(),
                        'product_id': contract.billing_product_id.id,
                        'description': _('PestOps service visit %s - %s') % (visit.name, visit.site_id.display_name),
                        'quantity': 1,
                        'unit_price': contract.amount,
                    })
                continue

            if contract.billing_frequency == 'once':
                exists = contract.billing_item_ids.filtered(lambda i: i.source_type == 'contract_period' and i.period_start == contract.start_date)
                if not exists:
                    BillingItem.create({
                        'name': _('Contract %s') % contract.code,
                        'contract_id': contract.id,
                        'source_type': 'contract_period',
                        'period_start': contract.start_date,
                        'period_end': contract.end_date or contract.start_date,
                        'invoice_date': contract.start_date,
                        'product_id': contract.billing_product_id.id,
                        'description': _('PestOps contract %s - %s') % (contract.code, contract.name),
                        'quantity': 1,
                        'unit_price': contract.amount,
                    })
                continue

            horizon_end = contract._billing_horizon_end()
            cursor = contract.start_date
            existing_periods = {
                (item.period_start, item.period_end)
                for item in contract.billing_item_ids.filtered(lambda i: i.source_type == 'contract_period')
            }
            while cursor <= horizon_end:
                period_end = min(contract._billing_period_end(cursor), horizon_end)
                if contract.end_date:
                    period_end = min(period_end, contract.end_date)
                if (cursor, period_end) not in existing_periods:
                    BillingItem.create({
                        'name': _('%s - %s to %s') % (contract.code, cursor, period_end),
                        'contract_id': contract.id,
                        'source_type': 'contract_period',
                        'period_start': cursor,
                        'period_end': period_end,
                        'invoice_date': cursor,
                        'product_id': contract.billing_product_id.id,
                        'description': _('PestOps contract %s - service period %s to %s') % (contract.code, cursor, period_end),
                        'quantity': 1,
                        'unit_price': contract.amount,
                    })
                next_cursor = period_end + timedelta(days=1)
                if next_cursor <= cursor:
                    break
                cursor = next_cursor

        return True

    def action_generate_invoices(self):
        self.ensure_one()
        self.action_prepare_billing()
        items = self.billing_item_ids.filtered(lambda i: i.state == 'to_invoice' and i.invoice_date <= fields.Date.context_today(self))
        if not items:
            raise UserError(_('There are no billing items ready to invoice.'))
        invoices = items._generate_invoices()
        if invoices:
            return {
                'type': 'ir.actions.act_window',
                'name': _('PestOps Invoices'),
                'res_model': 'account.move',
                'view_mode': 'list,form',
                'domain': [('id', 'in', invoices.ids)],
            }
        return True

    @api.model
    def _cron_prepare_billing(self):
        contracts = self.search([('state', 'in', ('confirmed', 'to_renew'))])
        for contract in contracts:
            try:
                contract.action_prepare_billing()
            except UserError:
                continue
        return True

    def action_view_billing_items(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Billing Items'),
            'res_model': 'pest.billing.item',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
        }

    def action_view_billing_invoices(self):
        self.ensure_one()
        invoice_ids = self.billing_item_ids.mapped('invoice_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', invoice_ids)],
        }

