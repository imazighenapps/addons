from odoo import fields, models


class PestZone(models.Model):
    _name = 'pest.zone'
    _description = 'Pest Control Zone'
    _order = 'site_id, name'

    name = fields.Char(required=True)
    code = fields.Char()
    site_id = fields.Many2one(
        'pest.site',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(
        related='site_id.company_id',
        store=True,
        index=True,
    )
    zone_type = fields.Selection(
        [
            ('kitchen', 'Kitchen'),
            ('cold_room', 'Cold Room'),
            ('restaurant', 'Restaurant'),
            ('warehouse', 'Warehouse'),
            ('production', 'Production Area'),
            ('office', 'Office'),
            ('outdoor', 'Outdoor'),
            ('waste', 'Waste Area'),
            ('other', 'Other'),
        ],
        default='other',
    )
    risk_level_id = fields.Many2one('pest.risk.level', ondelete='restrict')
    surface = fields.Float()
    active = fields.Boolean(default=True)
    description = fields.Text()

    control_point_ids = fields.One2many('pest.control.point', 'zone_id')
    plan_line_ids = fields.One2many('pest.treatment.plan.line', 'zone_id')
