from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestVisit(models.Model):
    _inherit = 'pest.visit'

    schedule_conflict_count = fields.Integer(
        string='Schedule Conflicts',
        compute='_compute_schedule_conflict_count',
        search='_search_schedule_conflict_count',
        help='Number of other active visits assigned to the same technician that overlap this visit.',
    )
    schedule_has_conflict = fields.Boolean(
        string='Schedule Conflict',
        compute='_compute_schedule_conflict_count',
    )

    def _get_schedule_conflicts(self):
        self.ensure_one()
        if not self.technician_id or not self.scheduled_start or not self.scheduled_end:
            return self.env['pest.visit']
        return self.search([
            ('id', '!=', self.id),
            ('technician_id', '=', self.technician_id.id),
            ('state', 'in', ('draft', 'scheduled', 'in_progress')),
            ('scheduled_start', '!=', False),
            ('scheduled_end', '!=', False),
            ('scheduled_start', '<', self.scheduled_end),
            ('scheduled_end', '>', self.scheduled_start),
        ], order='scheduled_start asc, id asc')

    def _search_schedule_conflict_count(self, operator, value):
        if operator not in ('>', '>=', '=', '!=', '<=', '<'):
            return [('id', '=', 0)]
        candidates = self.search([
            ('technician_id', '!=', False),
            ('scheduled_start', '!=', False),
            ('scheduled_end', '!=', False),
            ('state', 'in', ('draft', 'scheduled', 'in_progress')),
        ])
        conflict_ids = set()
        for visit in candidates:
            if visit._get_schedule_conflicts():
                conflict_ids.add(visit.id)
        # The field is a boolean-like conflict indicator for the business filter.
        # Search operators are interpreted against 0/1 presence rather than an exact count.
        target = float(value or 0)
        if operator == '>' and target == 0:
            return [('id', 'in', list(conflict_ids))]
        if operator == '>=' and target <= 1:
            return [('id', 'in', list(conflict_ids))]
        if operator == '=':
            return [('id', 'in' if target > 0 else 'not in', list(conflict_ids))]
        if operator == '!=':
            return [('id', 'not in' if target > 0 else 'in', list(conflict_ids))]
        if operator == '<' and target <= 1:
            return [('id', 'not in', list(conflict_ids))]
        if operator == '<=' and target < 1:
            return [('id', 'not in', list(conflict_ids))]
        return [('id', '=', 0)]

    @api.depends('technician_id', 'scheduled_start', 'scheduled_end', 'state')
    def _compute_schedule_conflict_count(self):
        for visit in self:
            conflicts = visit._get_schedule_conflicts()
            visit.schedule_conflict_count = len(conflicts)
            visit.schedule_has_conflict = bool(conflicts)

    @api.constrains('technician_id', 'scheduled_start', 'scheduled_end', 'state')
    def _check_scheduled_overlap(self):
        for visit in self:
            if visit.state in ('scheduled', 'in_progress'):
                conflicts = visit._get_schedule_conflicts()
                if conflicts:
                    names = ', '.join(conflicts.mapped('name')[:5])
                    if len(conflicts) > 5:
                        names += ', ...'
                    raise ValidationError(_(
                        'Technician %(technician)s has an overlapping PestOps visit: %(visits)s.'
                    ) % {
                        'technician': visit.technician_id.display_name,
                        'visits': names,
                    })

    def _ensure_no_schedule_conflict(self):
        for visit in self:
            conflicts = visit._get_schedule_conflicts()
            if conflicts:
                names = ', '.join(conflicts.mapped('name')[:5])
                raise UserError(_(
                    'Cannot schedule %(visit)s because technician %(technician)s already has an overlapping visit: %(visits)s.'
                ) % {
                    'visit': visit.display_name,
                    'technician': visit.technician_id.display_name,
                    'visits': names,
                })

    def action_schedule(self):
        for visit in self:
            if visit.technician_id and visit.scheduled_start and visit.scheduled_end:
                visit._ensure_no_schedule_conflict()
        return super().action_schedule()

    def action_start(self):
        for visit in self:
            if visit.technician_id and visit.scheduled_start and visit.scheduled_end:
                visit._ensure_no_schedule_conflict()
        return super().action_start()

    def action_check_schedule_conflicts(self):
        self.ensure_one()
        conflicts = self._get_schedule_conflicts()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Conflicts'),
            'res_model': 'pest.visit',
            'view_mode': 'list,form',
            'views': [
                (self.env.ref('pestops_calendar.view_pest_visit_conflict_list').id, 'list'),
                (self.env.ref('pestops_core.view_pest_visit_form').id, 'form'),
            ],
            'domain': [('id', 'in', conflicts.ids)],
            'context': {'create': False},
        }
