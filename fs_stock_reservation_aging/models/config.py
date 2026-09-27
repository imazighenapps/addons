from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockReservationAgingConfig(models.Model):
    _name = 'fs.stock.reservation.aging.config'
    _description = 'Stock Reservation Aging Configuration'
    _check_company_auto = True

    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company,
        index=True, ondelete='cascade',
    )
    aging_days = fields.Integer(default=7, required=True)
    critical_days = fields.Integer(default=30, required=True)

    _company_unique = models.Constraint(
        'unique (company_id)',
        'Only one reservation aging configuration is allowed per company.',
    )
    _days_valid = models.Constraint(
        'check(aging_days > 0 and critical_days >= aging_days)',
        'Aging and critical thresholds must be positive and ordered.',
    )

    @api.constrains('aging_days', 'critical_days')
    def _check_days(self):
        for record in self:
            if record.aging_days <= 0 or record.critical_days < record.aging_days:
                raise ValidationError('Aging and critical thresholds are invalid.')
