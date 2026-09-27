from odoo import api, fields, models


class MrpReadinessConfig(models.Model):
    _name = 'fs.mrp.readiness.config'
    _description = 'MRP Readiness Configuration'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, ondelete='cascade')
    check_workcenters = fields.Boolean(default=True)
    blocking_policy = fields.Selection(
        [('block', 'Block Production'), ('warn', 'Warn Only')],
        default='block',
        required=True,
    )

    _company_unique = models.Constraint(
        'unique (company_id)',
        'Only one configuration per company is allowed.',
    )
