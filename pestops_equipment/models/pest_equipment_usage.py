from odoo import api, fields, models, _


class PestEquipmentUsage(models.Model):
    _name = 'pest.equipment.usage'
    _description = 'PestOps Equipment Usage on Visit'
    _order = 'date desc, id desc'

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('pest.equipment.usage'), readonly=True, copy=False)
    equipment_id = fields.Many2one('pest.equipment', required=True, ondelete='restrict', tracking=True)
    visit_id = fields.Many2one('pest.visit', required=True, ondelete='cascade', tracking=True)
    technician_id = fields.Many2one('res.users', related='visit_id.technician_id', store=True, readonly=True)
    site_id = fields.Many2one('pest.site', related='visit_id.site_id', store=True, readonly=True)
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    notes = fields.Text()

    _sql_constraints = [
        ('equipment_visit_unique', 'unique(equipment_id, visit_id)', 'An equipment can only be logged once per visit.'),
    ]

    @api.constrains('equipment_id', 'visit_id')
    def _check_status(self):
        for rec in self:
            if rec.equipment_id.status in ('retired', 'out_of_service'):
                # Keep historical logs valid; reject only future creation.
                if rec.visit_id and rec.visit_id.state not in ('done', 'cancelled'):
                    from odoo.exceptions import ValidationError
                    raise ValidationError(_('An out-of-service or retired equipment cannot be used on an active visit.'))
