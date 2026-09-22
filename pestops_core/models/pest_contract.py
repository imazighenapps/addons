from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestContract(models.Model):
    _name = 'pest.contract'
    _description = 'Pest Control Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, id desc'

    name = fields.Char(
        required=True,
        tracking=True,
    )
    code = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.contract'),
        readonly=True,
        copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    start_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    end_date = fields.Date(tracking=True)

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('suspended', 'Suspended'),
            ('to_renew', 'To Renew'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )

    service_type = fields.Selection(
        [
            ('preventive', 'Preventive Pest Control'),
            ('curative', 'Curative Pest Control'),
            ('integrated', 'Integrated Pest Management'),
            ('disinfection', 'Disinfection'),
            ('fumigation', 'Fumigation'),
            ('other', 'Other'),
        ],
        default='preventive',
        required=True,
    )

    responsible_id = fields.Many2one(
        'res.users',
        string='Contract Responsible',
        default=lambda self: self.env.user,
    )

    default_frequency_type = fields.Selection(
        [
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months'),
        ],
        default=lambda self: self.env.company.pestops_default_frequency_type or 'weeks',
        required=True,
    )
    default_frequency_number = fields.Integer(
        default=lambda self: self.env.company.pestops_default_frequency_number or 2,
        required=True,
    )
    default_visit_duration_minutes = fields.Integer(
        default=lambda self: self.env.company.pestops_default_visit_duration_minutes or 60,
        required=True,
    )
    default_technician_id = fields.Many2one(
        'res.users',
        string='Default Technician',
    )

    site_line_ids = fields.One2many(
        'pest.contract.site',
        'contract_id',
        copy=True,
    )

    plan_ids = fields.One2many(
        'pest.treatment.plan',
        'contract_id',
        readonly=True,
    )
    visit_ids = fields.One2many(
        'pest.visit',
        'contract_id',
        readonly=True,
    )

    site_count = fields.Integer(compute='_compute_counts')
    plan_count = fields.Integer(compute='_compute_counts')
    visit_count = fields.Integer(compute='_compute_counts')

    amount = fields.Monetary(string='Contract Amount')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    billing_frequency = fields.Selection(
        [
            ('once', 'One-off'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('annual', 'Annual'),
            ('per_visit', 'Per Visit'),
        ],
        default='monthly',
        required=True,
    )
    billing_notes = fields.Text(
        help='Informational billing instructions for the Community core. '
             'Accounting/Sales integration is added by optional modules.'
    )

    notes = fields.Html()

    @api.depends('site_line_ids', 'plan_ids', 'visit_ids')
    def _compute_counts(self):
        for contract in self:
            contract.site_count = len(contract.site_line_ids)
            contract.plan_count = len(contract.plan_ids)
            contract.visit_count = len(contract.visit_ids)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for contract in self:
            if contract.end_date and contract.end_date < contract.start_date:
                raise ValidationError(
                    _('Contract end date must be on or after the start date.')
                )

    @api.constrains('default_frequency_number', 'default_visit_duration_minutes')
    def _check_frequency(self):
        for contract in self:
            if contract.default_frequency_number <= 0:
                raise ValidationError(
                    _('Default frequency must be greater than zero.')
                )
            if contract.default_visit_duration_minutes <= 0:
                raise ValidationError(
                    _('Default visit duration must be greater than zero.')
                )

    @api.constrains('site_line_ids')
    def _check_sites(self):
        for contract in self:
            sites = contract.site_line_ids.mapped('site_id')
            if len(sites) != len(contract.site_line_ids):
                raise ValidationError(
                    _('A site can only appear once in a contract.')
                )

    def action_confirm(self):
        for contract in self:
            if not contract.site_line_ids:
                raise UserError(
                    _('Add at least one site before confirming the contract.')
                )
            if contract.state not in ('draft', 'to_renew'):
                continue

            contract.write({'state': 'confirmed'})
            contract._create_or_update_treatment_plans()

    def action_suspend(self):
        for contract in self:
            if contract.state != 'confirmed':
                raise UserError(
                    _('Only confirmed contracts can be suspended.')
                )
            contract.write({'state': 'suspended'})

    def action_resume(self):
        for contract in self:
            if contract.state != 'suspended':
                raise UserError(
                    _('Only suspended contracts can be resumed.')
                )
            contract.write({'state': 'confirmed'})

    def action_set_to_renew(self):
        self.write({'state': 'to_renew'})

    def action_cancel(self):
        for contract in self:
            if contract.state == 'expired':
                raise UserError(_('An expired contract cannot be cancelled.'))
            contract.write({'state': 'cancelled'})
            contract.plan_ids.write({'active': False})

    def _create_or_update_treatment_plans(self):
        Plan = self.env['pest.treatment.plan']

        for contract in self:
            for line in contract.site_line_ids:
                frequency_type = (
                    line.frequency_type or contract.default_frequency_type
                )
                frequency_number = (
                    line.frequency_number or contract.default_frequency_number
                )
                duration = (
                    line.visit_duration_minutes
                    or contract.default_visit_duration_minutes
                )
                technician = (
                    line.technician_id
                    or contract.default_technician_id
                    or False
                )

                existing = Plan.search([
                    ('contract_id', '=', contract.id),
                    ('contract_site_line_id', '=', line.id),
                ], limit=1)

                vals = {
                    'name': f'{contract.name} - {line.site_id.name}',
                    'site_id': line.site_id.id,
                    'contract_id': contract.id,
                    'contract_site_line_id': line.id,
                    'start_date': contract.start_date,
                    'end_date': contract.end_date,
                    'frequency_type': frequency_type,
                    'frequency_number': frequency_number,
                    'visit_duration_minutes': duration,
                    'visit_horizon_days': line.visit_horizon_days,
                    'technician_id': technician.id if technician else False,
                    'responsible_id': contract.responsible_id.id,
                    'active': contract.state == 'confirmed',
                }

                if existing:
                    existing.write(vals)
                else:
                    existing = Plan.create(vals)

                line.plan_id = existing.id

            contract.plan_ids.filtered(
                lambda p: p.contract_site_line_id.id not in contract.site_line_ids.ids
            ).write({'active': False})

    def action_generate_visits(self):
        self.ensure_one()
        self._create_or_update_treatment_plans()
        self.plan_ids.filtered('active').action_generate_visits()
        return True

    def action_view_sites(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contract Sites'),
            'res_model': 'pest.contract.site',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
        }

    def action_view_plans(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Treatment Plans'),
            'res_model': 'pest.treatment.plan',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
        }

    def action_view_visits(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Visits'),
            'res_model': 'pest.visit',
            'view_mode': 'list,form,calendar',
            'domain': [('contract_id', '=', self.id)],
        }

    @api.model
    def _cron_contract_state(self):
        today = fields.Date.context_today(self)
        confirmed = self.search([
            ('state', '=', 'confirmed'),
            ('end_date', '!=', False),
            ('end_date', '<', today),
        ])
        confirmed.write({'state': 'expired'})
        confirmed.mapped('plan_ids').write({'active': False})

        to_renew = self.search([
            ('state', '=', 'confirmed'),
            ('end_date', '!=', False),
            ('end_date', '>=', today),
        ])
        threshold = 30
        to_renew.filtered(
            lambda c: (c.end_date - today).days <= threshold
        ).write({'state': 'to_renew'})

        return True


class PestContractSite(models.Model):
    _name = 'pest.contract.site'
    _description = 'Pest Contract Site'
    _order = 'sequence, id'

    contract_id = fields.Many2one(
        'pest.contract',
        required=True,
        ondelete='cascade',
    )
    site_id = fields.Many2one(
        'pest.site',
        required=True,
        ondelete='restrict',
        domain="[('partner_id', '=', parent.partner_id)]",
    )
    company_id = fields.Many2one(
        related='contract_id.company_id',
        store=True,
        index=True,
    )
    sequence = fields.Integer(default=10)

    frequency_type = fields.Selection(
        [
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months'),
        ],
        help='Leave empty to use the contract default.',
    )
    frequency_number = fields.Integer()
    visit_duration_minutes = fields.Integer()
    technician_id = fields.Many2one(
        'res.users',
        string='Technician',
    )
    visit_horizon_days = fields.Integer(
        default=60,
        required=True,
    )

    plan_id = fields.Many2one(
        'pest.treatment.plan',
        readonly=True,
        copy=False,
    )

    _sql_constraints = [
        (
            'contract_site_unique',
            'unique(contract_id, site_id)',
            'A site can only be added once to a contract.',
        ),
    ]

    @api.constrains('frequency_number', 'visit_duration_minutes', 'visit_horizon_days')
    def _check_positive_values(self):
        for line in self:
            if line.frequency_number and line.frequency_number <= 0:
                raise ValidationError(
                    _('Site frequency must be greater than zero.')
                )
            if line.visit_duration_minutes and line.visit_duration_minutes <= 0:
                raise ValidationError(
                    _('Visit duration must be greater than zero.')
                )
            if line.visit_horizon_days <= 0:
                raise ValidationError(
                    _('Visit generation horizon must be greater than zero.')
                )
