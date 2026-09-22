from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PestQualityAction(models.Model):
    _name = 'pest.quality.action'
    _description = 'PestOps Corrective / Preventive Action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'due_date asc, id desc'

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('pest.quality.action'), readonly=True, copy=False)
    nonconformity_id = fields.Many2one('pest.quality.nonconformity', required=True, ondelete='cascade', tracking=True)
    visit_id = fields.Many2one(related='nonconformity_id.visit_id', store=True, index=True)
    site_id = fields.Many2one(related='nonconformity_id.site_id', store=True, index=True)
    company_id = fields.Many2one(related='nonconformity_id.company_id', store=True, index=True)
    action_type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive'),
    ], default='corrective', required=True, tracking=True)
    state = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='todo', required=True, tracking=True)
    description = fields.Text(required=True)
    result = fields.Text()
    responsible_user_id = fields.Many2one('res.users', tracking=True)
    due_date = fields.Date(tracking=True)
    started_date = fields.Datetime(readonly=True)
    closed_date = fields.Datetime(readonly=True)
    evidence_ids = fields.One2many('pest.quality.evidence', 'action_id')
    evidence_count = fields.Integer(compute='_compute_counts')

    @api.depends('evidence_ids')
    def _compute_counts(self):
        for record in self:
            record.evidence_count = len(record.evidence_ids)

    def action_start(self):
        for record in self:
            record.write({'state': 'in_progress', 'started_date': fields.Datetime.now()})

    def action_done(self):
        for record in self:
            if not record.result:
                raise UserError(_('Please record the result before completing the action.'))
            record.write({'state': 'done', 'closed_date': fields.Datetime.now()})

    def action_cancel(self):
        self.write({'state': 'cancelled', 'closed_date': fields.Datetime.now()})
