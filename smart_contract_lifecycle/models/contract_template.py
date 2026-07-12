from odoo import api, fields, models, _


class ContractTemplate(models.Model):
    _name = 'contract.template'
    _description = 'Contract Template'
    _order = 'name'

    name = fields.Char(string='Template Name', required=True)
    contract_type = fields.Selection([
        ('customer', 'Customer Contract'),
        ('supplier', 'Vendor Contract'),
        ('partnership', 'Partnership'),
        ('nda', 'NDA / Confidentiality'),
        ('employment', 'Employment Contract'),
        ('lease', 'Lease / Rental'),
        ('service', 'Service Agreement'),
        ('other', 'Other'),
    ], string='Contract Type', required=True, default='customer')

    content = fields.Html(
        string='Template Content',
        help='Body of the contract. Available variables: '
             '{{partner_name}}, {{date_start}}, {{date_end}}, '
             '{{amount_total}}, {{company_name}}, {{user_name}}, {{contract_ref}}',
    )
    notice_days = fields.Integer(string='Default Notice Period (days)', default=30)
    renewal_type = fields.Selection([
        ('none', 'No Renewal'),
        ('manual', 'Manual Renewal'),
        ('automatic', 'Automatic Renewal'),
    ], string='Renewal', default='manual')
    renewal_duration = fields.Integer(string='Renewal Duration', default=12)
    renewal_duration_unit = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years'),
    ], string='Unit', default='months')

    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    usage_count = fields.Integer(
        string='Usages',
        compute='_compute_usage_count',
    )

    def _compute_usage_count(self):
        for tmpl in self:
            tmpl.usage_count = self.env['contract.contract'].search_count(
                [('template_id', '=', tmpl.id)]
            )

    def action_view_contracts(self):
        """Opens the list of contracts using this template."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contracts — %s') % self.name,
            'res_model': 'contract.contract',
            'view_mode': 'list,form',
            'domain': [('template_id', '=', self.id)],
            'context': {'default_template_id': self.id},
        }


class ContractMilestone(models.Model):
    _name = 'contract.milestone'
    _description = 'Contract Milestone / Deliverable'
    _order = 'date_due'

    contract_id = fields.Many2one(
        'contract.contract',
        string='Contract',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Milestone Description', required=True)
    date_due = fields.Date(string='Due Date', required=True)
    date_done = fields.Date(string='Completion Date')

    state = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('late', 'Late'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending', compute='_compute_state', store=True)

    is_cancelled = fields.Boolean(string='Cancelled', default=False)

    amount = fields.Monetary(
        string='Associated Amount',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        related='contract_id.currency_id',
        store=True,
    )
    responsible_id = fields.Many2one('res.users', string='Responsible')
    notes = fields.Text(string='Notes')

    @api.depends('date_due', 'date_done', 'is_cancelled')
    def _compute_state(self):
        today = fields.Date.today()
        for rec in self:
            if rec.is_cancelled:
                rec.state = 'cancelled'
            elif rec.date_done:
                rec.state = 'done'
            elif rec.date_due and rec.date_due < today:
                rec.state = 'late'
            else:
                rec.state = 'pending'

    def action_mark_done(self):
        """Sets the completion date; the status is recalculated automatically."""
        self.write({'date_done': fields.Date.today(), 'is_cancelled': False})

    def action_cancel(self):
        """Marks the milestone as cancelled."""
        self.write({'is_cancelled': True})

    def action_reactivate(self):
        """Clears the cancellation, returning to pending/late/done based on dates."""
        self.write({'is_cancelled': False})
