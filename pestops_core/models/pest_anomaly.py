from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PestAnomaly(models.Model):
    _name = 'pest.anomaly'
    _description = 'Pest Control Anomaly'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'severity desc, due_date asc, id desc'

    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.anomaly'),
        readonly=True,
        copy=False,
        tracking=True,
    )
    visit_id = fields.Many2one(
        'pest.visit', required=True, ondelete='cascade', index=True, tracking=True,
    )
    inspection_id = fields.Many2one('pest.inspection', ondelete='set null', index=True)
    inspection_line_id = fields.Many2one('pest.inspection.line', ondelete='set null', index=True)
    site_id = fields.Many2one(related='visit_id.site_id', store=True, index=True)
    company_id = fields.Many2one(related='site_id.company_id', store=True, index=True)
    zone_id = fields.Many2one('pest.zone', ondelete='restrict', index=True)
    control_point_id = fields.Many2one('pest.control.point', ondelete='restrict', index=True)
    technician_id = fields.Many2one(related='visit_id.technician_id', store=True)
    assigned_user_id = fields.Many2one('res.users', tracking=True)
    pest_id = fields.Many2one('pest.type', ondelete='restrict')

    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium', required=True, tracking=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='open', required=True, tracking=True)
    category = fields.Selection([
        ('activity', 'Pest Activity'),
        ('structural', 'Structural Issue'),
        ('hygiene', 'Hygiene Issue'),
        ('equipment', 'Equipment Issue'),
        ('other', 'Other'),
    ], default='activity', required=True)
    description = fields.Text(required=True)
    corrective_action = fields.Text()
    recommendation = fields.Text()
    due_date = fields.Date(tracking=True)
    detected_date = fields.Datetime(default=fields.Datetime.now, required=True)
    closed_date = fields.Datetime(readonly=True)
    attachment_image = fields.Image()
    reservice_id = fields.Many2one('pest.reservice', string='Re-Service', readonly=True)

    @api.onchange('severity')
    def _onchange_severity(self):
        if self.severity in ('high', 'critical') and not self.due_date:
            self.due_date = fields.Date.context_today(self)

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done', 'closed_date': fields.Datetime.now()})

    def action_cancel(self):
        self.write({'state': 'cancelled', 'closed_date': fields.Datetime.now()})

    def action_create_reservice(self):
        Reservice = self.env['pest.reservice']
        for anomaly in self:
            if anomaly.reservice_id:
                continue
            if not anomaly.visit_id:
                raise UserError(_('An anomaly must be linked to a visit before creating a re-service.'))
            reason = 'persistent_infestation' if anomaly.category == 'activity' else 'other'
            reservice = Reservice.create({
                'origin_visit_id': anomaly.visit_id.id,
                'requested_by': anomaly.site_id.partner_id.id,
                'reason': reason,
                'notes': anomaly.description,
                'state': 'open',
            })
            anomaly.reservice_id = reservice.id
        return True
