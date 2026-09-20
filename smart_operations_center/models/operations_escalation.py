from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SmartOperationsEscalation(models.Model):
    _name = 'smart.operations.escalation'
    _description = 'Operational Escalation Policy'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    first_delay_hours = fields.Float(default=24.0)
    second_delay_hours = fields.Float(default=48.0)
    first_user_id = fields.Many2one('res.users', ondelete='set null')
    second_user_id = fields.Many2one('res.users', ondelete='set null')
    notify_activity = fields.Boolean(default=True)


    @api.constrains('first_delay_hours', 'second_delay_hours')
    def _check_delays(self):
        for policy in self:
            if policy.first_delay_hours < 0 or policy.second_delay_hours < 0:
                raise ValidationError(_('Escalation delays cannot be negative.'))
            if policy.second_delay_hours and policy.first_delay_hours and policy.second_delay_hours < policy.first_delay_hours:
                raise ValidationError(_('The second escalation delay must be greater than or equal to the first delay.'))
