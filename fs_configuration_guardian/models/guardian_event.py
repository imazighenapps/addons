from odoo import fields, models


class GuardianEvent(models.Model):
    _name = 'fs.guardian.event'
    _description = 'Configuration Guardian Event'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    level = fields.Selection([('info', 'Info'), ('warning', 'Warning'), ('critical', 'Critical')], default='info')
    message = fields.Text(required=True)
    baseline_id = fields.Many2one('fs.guardian.baseline', ondelete='cascade')
    change_id = fields.Many2one('fs.guardian.change', ondelete='cascade')
