from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CustomerOrderSnapshotConfig(models.Model):
    _name = 'fs.customer.order.snapshot.config'
    _description = 'Customer Order Snapshot Configuration'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, ondelete='cascade')
    lookback_days = fields.Integer(default=365, required=True)
    max_orders = fields.Integer(default=5, required=True)
    include_prices = fields.Boolean(default=True)
    include_discounts = fields.Boolean(default=True)

    _company_unique = models.Constraint(
        'unique (company_id)',
        'Only one customer order snapshot configuration is allowed per company.',
    )

    @api.constrains('lookback_days', 'max_orders')
    def _check_limits(self):
        for rec in self:
            if rec.lookback_days <= 0:
                raise ValidationError('Lookback period must be greater than zero.')
            if not 1 <= rec.max_orders <= 100:
                raise ValidationError('Maximum orders must be between 1 and 100.')
