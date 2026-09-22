from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PestQualityNonconformity(models.Model):
    _name = 'pest.quality.nonconformity'
    _description = 'PestOps Quality Non-Conformity'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'severity desc, due_date asc, id desc'

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('pest.quality.nonconformity'), readonly=True, copy=False)
    check_id = fields.Many2one('pest.quality.check', required=True, ondelete='cascade', tracking=True)
    check_line_id = fields.Many2one('pest.quality.check.line', ondelete='set null')
    visit_id = fields.Many2one(related='check_id.visit_id', store=True, index=True)
    site_id = fields.Many2one(related='check_id.site_id', store=True, index=True)
    technician_id = fields.Many2one(related='check_id.technician_id', store=True)
    company_id = fields.Many2one(related='check_id.company_id', store=True, index=True)
    procedure_id = fields.Many2one(related='check_id.procedure_id', store=True)
    checklist_id = fields.Many2one(related='check_id.checklist_id', store=True)
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium', required=True, tracking=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], default='open', required=True, tracking=True)
    description = fields.Text(required=True)
    root_cause = fields.Text()
    corrective_action = fields.Text()
    preventive_action = fields.Text()
    responsible_user_id = fields.Many2one('res.users', tracking=True)
    detected_date = fields.Datetime(default=fields.Datetime.now, required=True)
    due_date = fields.Date(tracking=True)
    resolved_date = fields.Datetime(readonly=True)
    closed_date = fields.Datetime(readonly=True)
    action_ids = fields.One2many('pest.quality.action', 'nonconformity_id')
    evidence_ids = fields.One2many('pest.quality.evidence', 'nonconformity_id')
    action_count = fields.Integer(compute='_compute_counts')
    open_action_count = fields.Integer(compute='_compute_counts')
    evidence_count = fields.Integer(compute='_compute_counts')

    @api.depends('action_ids', 'action_ids.state', 'evidence_ids')
    def _compute_counts(self):
        for record in self:
            record.action_count = len(record.action_ids)
            record.open_action_count = len(record.action_ids.filtered(lambda a: a.state != 'done'))
            record.evidence_count = len(record.evidence_ids)

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_resolve(self):
        for record in self:
            open_actions = record.action_ids.filtered(lambda a: a.state != 'done')
            if open_actions:
                raise UserError(_('All corrective/preventive actions must be completed before resolving the non-conformity.'))
            record.write({'state': 'resolved', 'resolved_date': fields.Datetime.now()})

    def action_close(self):
        for record in self:
            if record.state != 'resolved':
                raise UserError(_('A non-conformity must be resolved before it can be closed.'))
            record.write({'state': 'closed', 'closed_date': fields.Datetime.now()})

    def action_cancel(self):
        self.write({'state': 'cancelled', 'closed_date': fields.Datetime.now()})

    def action_create_action(self):
        self.ensure_one()
        action = self.env['pest.quality.action'].create({
            'nonconformity_id': self.id,
            'action_type': 'corrective',
            'description': self.corrective_action or self.description,
            'responsible_user_id': self.responsible_user_id.id,
            'due_date': self.due_date,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Corrective Action'),
            'res_model': 'pest.quality.action',
            'view_mode': 'form',
            'res_id': action.id,
        }

    @api.model
    def _cron_quality_due_alerts(self):
        today = fields.Date.context_today(self)
        records = self.search([
            ('state', 'in', ('open', 'in_progress')),
            ('due_date', '!=', False),
            ('due_date', '<=', today),
            ('responsible_user_id', '!=', False),
        ])
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return True
        for record in records:
            summary = _('Overdue Quality Non-Conformity')
            existing = self.env['mail.activity'].search_count([
                ('res_model', '=', self._name),
                ('res_id', '=', record.id),
                ('activity_type_id', '=', activity_type.id),
                ('summary', '=', summary),
            ])
            if existing:
                continue
            self.env['mail.activity'].create({
                'activity_type_id': activity_type.id,
                'res_model_id': self.env['ir.model']._get_id(self._name),
                'res_id': record.id,
                'user_id': record.responsible_user_id.id,
                'summary': summary,
                'note': _('Non-conformity %s is overdue.') % record.name,
                'date_deadline': today,
            })
        return True
