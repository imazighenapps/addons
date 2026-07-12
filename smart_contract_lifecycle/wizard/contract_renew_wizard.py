from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class ContractRenewWizard(models.TransientModel):
    _name = 'contract.renew.wizard'
    _description = 'Contract Renewal Wizard'

    contract_id = fields.Many2one(
        'contract.contract',
        string='Contract to Renew',
        required=True,
        readonly=True,
    )
    current_end_date = fields.Date(
        related='contract_id.date_end',
        string="Current Expiry Date",
        readonly=True,
    )
    partner_id = fields.Many2one(
        related='contract_id.partner_id',
        readonly=True,
    )
    new_date_start = fields.Date(
        string='New Start Date',
        required=True,
    )
    new_date_end = fields.Date(string='New End Date')
    duration = fields.Integer(string='Duration', default=12)
    duration_unit = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years'),
    ], string='Unit', default='months')
    new_amount = fields.Monetary(
        string='New Contract Value',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        related='contract_id.currency_id',
        readonly=True,
    )
    notes = fields.Text(string='Renewal Notes')
    keep_milestones = fields.Boolean(string='Copy Milestones', default=False)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        contract_id = self.env.context.get('default_contract_id')
        if contract_id:
            contract = self.env['contract.contract'].browse(contract_id)
            if contract.date_end:
                res['new_date_start'] = contract.date_end + relativedelta(days=1)
                if contract.renewal_duration and contract.renewal_duration_unit:
                    unit = contract.renewal_duration_unit
                    dur = contract.renewal_duration
                    delta_map = {
                        'days': relativedelta(days=dur),
                        'months': relativedelta(months=dur),
                        'years': relativedelta(years=dur),
                    }
                    delta = delta_map.get(unit, relativedelta(months=12))
                    res['new_date_end'] = (
                        res['new_date_start'] + delta - relativedelta(days=1)
                    )
                    res['duration'] = contract.renewal_duration
                    res['duration_unit'] = contract.renewal_duration_unit
            res['new_amount'] = contract.amount_total
        return res

    @api.onchange('new_date_start', 'duration', 'duration_unit')
    def _onchange_compute_end(self):
        if self.new_date_start and self.duration and self.duration_unit:
            delta_map = {
                'days': relativedelta(days=self.duration),
                'months': relativedelta(months=self.duration),
                'years': relativedelta(years=self.duration),
            }
            delta = delta_map.get(self.duration_unit, relativedelta(months=12))
            self.new_date_end = self.new_date_start + delta - relativedelta(days=1)

    @api.constrains('new_date_start', 'new_date_end')
    def _check_dates(self):
        for rec in self:
            if rec.new_date_end and rec.new_date_start and rec.new_date_end < rec.new_date_start:
                raise ValidationError(
                    _('The end date must be later than the start date.')
                )

    def action_renew(self):
        """Creates the renewed contract, optionally carries over the
        milestones, and marks the original contract as renewed."""
        self.ensure_one()
        contract = self.contract_id
        if not self.new_date_start:
            raise UserError(_('The start date is required.'))

        new_contract = contract.copy({
            'title': _('%s (Renewal)') % contract.title,
            'date_start': self.new_date_start,
            'date_end': self.new_date_end,
            'parent_contract_id': contract.id,
            'state': 'draft',
            'amount_total': self.new_amount or contract.amount_total,
            'milestone_ids': [(5, 0, 0)],
        })
        new_contract.write({'version': contract.version + 1})

        if self.keep_milestones and contract.milestone_ids:
            delta = self.new_date_start - (contract.date_start or self.new_date_start)
            for milestone in contract.milestone_ids:
                new_due = (
                    milestone.date_due + delta
                    if milestone.date_due else milestone.date_due
                )
                self.env['contract.milestone'].create({
                    'contract_id': new_contract.id,
                    'name': milestone.name,
                    'date_due': new_due,
                    'amount': milestone.amount,
                    'responsible_id': milestone.responsible_id.id if milestone.responsible_id else False,
                    'notes': milestone.notes,
                })

        contract.write({'state': 'renewed'})
        contract.message_post(
            body=_(
                'Contract manually renewed by <strong>%s</strong> → '
                '<a href="/odoo/contracts/%s">%s</a>. %s'
            ) % (
                self.env.user.name,
                new_contract.id,
                new_contract.name,
                self.notes or '',
            ),
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _('New Contract'),
            'res_model': 'contract.contract',
            'res_id': new_contract.id,
            'view_mode': 'form',
        }
