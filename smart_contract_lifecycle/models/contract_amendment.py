from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ContractAmendment(models.Model):
    _name = 'contract.amendment'
    _description = 'Contract Amendment'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    contract_id = fields.Many2one(
        'contract.contract',
        string='Contract',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    partner_id = fields.Many2one(
        related='contract_id.partner_id',
        string='Partner',
        store=True,
    )
    date = fields.Date(
        string='Amendment Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    amendment_type = fields.Selection([
        ('extension', 'Term Extension'),
        ('financial', 'Financial Change'),
        ('scope', 'Scope Change'),
        ('termination', 'Termination Clause'),
        ('other', 'Other Change'),
    ], string='Amendment Type', required=True, default='other', tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Signature'),
        ('signed', 'Signed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    description = fields.Html(string='Amendment Description')

    new_date_end = fields.Date(string='New End Date')
    amount_change = fields.Monetary(
        string='Financial Impact',
        currency_field='currency_id',
        help='Positive amount = increase, negative = decrease.',
    )
    currency_id = fields.Many2one(
        related='contract_id.currency_id',
        store=True,
    )

    signed_date = fields.Date(string='Signature Date')
    signed_by = fields.Many2one('res.users', string='Signed By')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('contract.amendment') or 'New'
        return super().create(vals_list)

    def action_submit(self):
        """Submits the amendment for signature (draft → pending)."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only a draft amendment can be submitted."))
        self.write({'state': 'pending'})
        self.message_post(
            body=_("Amendment submitted for signature by <strong>%s</strong>.") % self.env.user.name,
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )

    def action_sign(self):
        """Signs the amendment and applies its changes to the parent contract."""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_("Only an amendment pending signature can be signed."))
        self.write({
            'state': 'signed',
            'signed_date': fields.Date.today(),
            'signed_by': self.env.user.id,
        })
        contract = self.contract_id
        vals = {}
        if self.new_date_end:
            vals['date_end'] = self.new_date_end
        if self.amount_change:
            vals['amount_total'] = contract.amount_total + self.amount_change
        if vals:
            contract.write(vals)
            contract.message_post(
                body=_('Amendment %s applied: %s') % (self.name, self.amendment_type),
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

    def action_cancel(self):
        self.ensure_one()
        if self.state == 'signed':
            raise UserError(_(
                "A signed amendment cannot be cancelled: its changes have "
                "already been applied to the contract. Create a new "
                "amendment to reverse them instead."
            ))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
