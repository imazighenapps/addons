from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestOpsSaleCreateContractWizard(models.TransientModel):
    _name = 'pestops.sale.create.contract.wizard'
    _description = 'Create PestOps Contract from Sales Order'

    sale_order_id = fields.Many2one(
        'sale.order',
        required=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        readonly=True,
    )

    start_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
    )
    end_date = fields.Date()

    frequency_type = fields.Selection(
        [
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months'),
        ],
        required=True,
        default='weeks',
    )
    frequency_number = fields.Integer(
        required=True,
        default=2,
    )
    visit_duration_minutes = fields.Integer(
        required=True,
        default=60,
    )
    technician_id = fields.Many2one('res.users')
    billing_frequency = fields.Selection(
        [
            ('once', 'One-off'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('annual', 'Annual'),
            ('per_visit', 'Per Visit'),
        ],
        required=True,
        default='monthly',
    )

    site_ids = fields.Many2many(
        'pest.site',
        string='Service Sites',
        required=True,
        domain="[('partner_id', '=', partner_id)]",
    )

    notes = fields.Text()

    @api.constrains('frequency_number', 'visit_duration_minutes')
    def _check_positive(self):
        for wizard in self:
            if wizard.frequency_number <= 0:
                raise ValidationError(_('Frequency must be greater than zero.'))
            if wizard.visit_duration_minutes <= 0:
                raise ValidationError(_('Visit duration must be greater than zero.'))

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for wizard in self:
            if wizard.end_date and wizard.end_date < wizard.start_date:
                raise ValidationError(
                    _('End date must be on or after start date.')
                )

    def action_create(self):
        self.ensure_one()

        if not self.site_ids:
            raise UserError(_('Select at least one service site.'))

        order = self.sale_order_id
        if order.pestops_contract_id:
            return order.action_open_pestops_contract()

        Contract = self.env['pest.contract']

        contract = Contract.create({
            'name': order.name,
            'partner_id': self.partner_id.id,
            'company_id': order.company_id.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'service_type': 'preventive',
            'responsible_id': order.user_id.id or self.env.user.id,
            'default_frequency_type': self.frequency_type,
            'default_frequency_number': self.frequency_number,
            'default_visit_duration_minutes': self.visit_duration_minutes,
            'default_technician_id': self.technician_id.id or False,
            'billing_frequency': self.billing_frequency,
            'amount': order.amount_total,
            'currency_id': order.currency_id.id,
            'notes': self.notes or False,
            'sale_order_id': order.id,
        })

        for site in self.site_ids:
            self.env['pest.contract.site'].create({
                'contract_id': contract.id,
                'site_id': site.id,
                'frequency_type': self.frequency_type,
                'frequency_number': self.frequency_number,
                'visit_duration_minutes': self.visit_duration_minutes,
                'technician_id': self.technician_id.id or False,
            })

        order.pestops_contract_id = contract.id

        # A quotation creates a draft contract. It is activated only when the
        # sales order is confirmed.
        return {
            'type': 'ir.actions.act_window',
            'name': _('PestOps Contract'),
            'res_model': 'pest.contract',
            'view_mode': 'form',
            'res_id': contract.id,
            'target': 'current',
        }
