from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderDuplicateConfig(models.Model):
    _name = 'fs.sale.order.duplicate.config'
    _description = 'Sales Order Duplicate Configuration'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, ondelete='cascade')
    lookback_days = fields.Integer(default=30, required=True)
    medium_threshold = fields.Integer(default=60, required=True)
    high_threshold = fields.Integer(default=80, required=True)
    amount_tolerance = fields.Monetary(default=0.0, currency_field='currency_id')
    quantity_tolerance = fields.Float(default=0.0, required=True)
    compare_reference = fields.Boolean(default=True)
    compare_lines = fields.Boolean(default=True)
    active = fields.Boolean(default=True)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)

    _company_unique = models.Constraint(
        'unique (company_id)',
        'Only one duplicate detection configuration is allowed per company.',
    )
    _thresholds_valid = models.Constraint(
        'check(lookback_days > 0 and medium_threshold >= 1 and high_threshold >= medium_threshold and high_threshold <= 100)',
        'Duplicate detection thresholds are invalid.',
    )
    _quantity_tolerance_valid = models.Constraint(
        'check(quantity_tolerance >= 0)',
        'Quantity tolerance cannot be negative.',
    )
    _amount_tolerance_valid = models.Constraint(
        'check(amount_tolerance >= 0)',
        'Amount tolerance cannot be negative.',
    )

    @api.onchange('company_id')
    def _onchange_company_id(self):
        for rec in self:
            if rec.company_id:
                rec.currency_id = rec.company_id.currency_id
