from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    contract_id = fields.Many2one(
        'contract.contract',
        string='Related Contract',
        ondelete='set null',
        tracking=True,
        copy=False,
        help='Contract this invoice is linked to.',
    )
