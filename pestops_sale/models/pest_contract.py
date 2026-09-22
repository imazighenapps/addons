from odoo import fields, models


class PestContract(models.Model):
    _inherit = 'pest.contract'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        readonly=True,
        copy=False,
        index=True,
    )
