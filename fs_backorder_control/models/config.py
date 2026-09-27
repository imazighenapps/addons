from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BackorderControlConfig(models.Model):
    _name = 'fs.backorder.control.config'
    _description = 'Backorder Control Configuration'
    _check_company_auto = True

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        ondelete='cascade',
    )
    aging_days = fields.Integer(default=7, required=True)
    critical_days = fields.Integer(default=30, required=True)

    _company_unique = models.Constraint(
        'unique (company_id)',
        'Only one configuration per company is allowed.',
    )
    _thresholds_valid = models.Constraint(
        'check(aging_days > 0 and critical_days >= aging_days)',
        'Thresholds must be valid.',
    )

    @api.constrains('aging_days', 'critical_days')
    def _check_thresholds(self):
        for record in self:
            if record.aging_days <= 0 or record.critical_days < record.aging_days:
                raise ValidationError(_('Backorder aging thresholds are invalid.'))
