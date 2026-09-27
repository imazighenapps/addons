from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PickingExceptionConfig(models.Model):
    _name = 'fs.picking.exception.config'
    _description = 'Picking Exception Configuration'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, ondelete='cascade')
    overdue_minutes = fields.Integer(default=0, required=True)
    critical_after_days = fields.Integer(default=2, required=True)
    notification_mode = fields.Selection(
        [('none', 'No notification'), ('activity', 'Create activity')],
        default='activity',
        required=True,
    )
    notification_user_id = fields.Many2one('res.users', string='Notification User')

    _company_unique = models.Constraint(
        'unique (company_id)',
        'Only one configuration is allowed per company.',
    )

    @api.constrains('overdue_minutes', 'critical_after_days')
    def _check_thresholds(self):
        for rec in self:
            if rec.overdue_minutes < 0 or rec.critical_after_days < 0:
                raise ValidationError('Exception thresholds cannot be negative.')
