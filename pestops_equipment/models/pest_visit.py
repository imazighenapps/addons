from odoo import fields, models, _


class PestVisit(models.Model):
    _inherit = 'pest.visit'

    equipment_usage_ids = fields.One2many('pest.equipment.usage', 'visit_id', string='Equipment Used')
    equipment_usage_count = fields.Integer(compute='_compute_equipment_usage_count')

    def _compute_equipment_usage_count(self):
        for visit in self:
            visit.equipment_usage_count = len(visit.equipment_usage_ids)

    def action_add_equipment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Equipment Used'),
            'res_model': 'pest.equipment.usage',
            'view_mode': 'list,form',
            'domain': [('visit_id', '=', self.id)],
            'context': {
                'default_visit_id': self.id,
                'default_technician_id': self.technician_id.id if self.technician_id else False,
            },
        }
