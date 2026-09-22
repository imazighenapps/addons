from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PestEquipmentInspection(models.Model):
    _name = 'pest.equipment.inspection'
    _description = 'PestOps Equipment Inspection'
    _inherit = ['mail.thread']
    _order = 'scheduled_date desc, id desc'

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('pest.equipment.inspection'), readonly=True, copy=False)
    equipment_id = fields.Many2one('pest.equipment', required=True, ondelete='cascade', tracking=True)
    scheduled_date = fields.Date(required=True, default=fields.Date.context_today, tracking=True)
    completed_date = fields.Date(tracking=True)
    performed_by = fields.Many2one('res.users', string='Performed By', tracking=True)
    state = fields.Selection([
        ('open', 'Planned'),
        ('done', 'Passed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='open', required=True, tracking=True)
    frequency_days = fields.Integer(string='Repeat Every (Days)', default=90)
    next_due_date = fields.Date(compute='_compute_next_due', store=True)
    checklist = fields.Text()
    findings = fields.Text()
    corrective_action = fields.Text()

    @api.depends('scheduled_date', 'completed_date', 'frequency_days', 'state')
    def _compute_next_due(self):
        for rec in self:
            if rec.state in ('done', 'failed') and rec.completed_date and rec.frequency_days > 0:
                rec.next_due_date = fields.Date.add(rec.completed_date, days=rec.frequency_days)
            else:
                rec.next_due_date = rec.scheduled_date

    @api.constrains('frequency_days')
    def _check_frequency(self):
        for rec in self:
            if rec.frequency_days <= 0:
                raise ValidationError(_('Inspection frequency must be greater than zero.'))

    def action_pass(self):
        for rec in self:
            rec.write({
                'state': 'done',
                'completed_date': fields.Date.context_today(self),
                'performed_by': rec.performed_by.id if rec.performed_by else self.env.user.id,
            })

    def action_fail(self):
        for rec in self:
            rec.write({
                'state': 'failed',
                'completed_date': fields.Date.context_today(self),
                'performed_by': rec.performed_by.id if rec.performed_by else self.env.user.id,
            })
            rec.equipment_id.action_set_maintenance()

    def action_cancel(self):
        self.write({'state': 'cancelled'})
