from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PosCashReviewConfig(models.Model):
    _name = 'fs.pos.cash.review.config'
    _description = 'POS Cash Closing Review Configuration'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, ondelete='cascade')
    warning_amount = fields.Float(default=5.0, required=True)
    critical_amount = fields.Float(default=50.0, required=True)
    require_approval_before_close = fields.Boolean(default=True)

    _company_unique = models.Constraint(
        'unique (company_id)',
        'Only one POS closing review configuration is allowed per company.',
    )
    _thresholds_valid = models.Constraint(
        'check(warning_amount >= 0 and critical_amount >= warning_amount)',
        'Closing thresholds are invalid.',
    )

    @api.constrains('warning_amount', 'critical_amount')
    def _check_thresholds(self):
        for rec in self:
            if rec.warning_amount < 0 or rec.critical_amount < rec.warning_amount:
                raise ValidationError('Closing thresholds are invalid.')
