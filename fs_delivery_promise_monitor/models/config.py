from odoo import api, fields, models
from odoo.exceptions import ValidationError


class DeliveryPromiseMonitorConfig(models.Model):
    _name = 'fs.delivery.promise.monitor.config'
    _description = 'Delivery Promise Monitor Configuration'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, ondelete='cascade')
    warning_hours = fields.Float(default=24.0, required=True)
    notification_mode = fields.Selection(
        [('none', 'No notification'), ('activity', 'Create activity')],
        default='activity',
        required=True,
    )

    _company_unique = models.Constraint(
        'unique (company_id)',
        'Only one delivery promise configuration is allowed per company.',
    )

    @api.constrains('warning_hours')
    def _check_warning_hours(self):
        for rec in self:
            if rec.warning_hours <= 0:
                raise ValidationError('Warning window must be greater than zero.')
