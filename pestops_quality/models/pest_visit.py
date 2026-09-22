from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PestVisit(models.Model):
    _inherit = 'pest.visit'

    quality_check_ids = fields.One2many('pest.quality.check', 'visit_id', string='Quality Checks')
    quality_count = fields.Integer(compute='_compute_quality_counts')
    open_nonconformity_count = fields.Integer(compute='_compute_quality_counts')
    quality_required = fields.Boolean(default=False, tracking=True)

    @api.depends('quality_check_ids', 'quality_check_ids.nonconformity_ids.state')
    def _compute_quality_counts(self):
        for visit in self:
            visit.quality_count = len(visit.quality_check_ids)
            ncs = visit.quality_check_ids.mapped('nonconformity_ids')
            visit.open_nonconformity_count = len(ncs.filtered(lambda n: n.state in ('open', 'in_progress')))

    def _prepare_completion(self):
        super()._prepare_completion()
        for visit in self:
            if visit.quality_required and not visit.quality_check_ids.filtered(lambda c: c.state == 'done'):
                raise UserError(_('At least one completed quality check is required before completing this visit.'))

    def action_create_quality_check(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quality Check'),
            'res_model': 'pest.quality.check',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_visit_id': self.id,
                'default_site_id': self.site_id.id,
                'default_technician_id': self.technician_id.id,
            },
        }

    def action_view_quality_checks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quality Checks'),
            'res_model': 'pest.quality.check',
            'view_mode': 'list,form',
            'domain': [('visit_id', '=', self.id)],
            'context': {'default_visit_id': self.id, 'default_site_id': self.site_id.id},
        }
