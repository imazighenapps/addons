from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PestEquipmentMaintenance(models.Model):
    _name = 'pest.equipment.maintenance'
    _description = 'PestOps Equipment Maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'planned_date desc, id desc'

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('pest.equipment.maintenance'), readonly=True, copy=False)
    equipment_id = fields.Many2one('pest.equipment', required=True, ondelete='cascade', tracking=True)
    maintenance_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('calibration', 'Calibration'),
        ('inspection', 'Inspection Follow-up'),
        ('other', 'Other'),
    ], default='preventive', required=True, tracking=True)
    planned_date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    completed_date = fields.Date(tracking=True)
    performed_by = fields.Many2one('res.users', tracking=True)
    vendor = fields.Char()
    cost = fields.Monetary()
    currency_id = fields.Many2one('res.currency', related='equipment_id.company_id.currency_id', store=True, readonly=True)
    frequency_days = fields.Integer(default=180)
    next_due_date = fields.Date(compute='_compute_next_due', store=True)
    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='planned', required=True, tracking=True)
    description = fields.Text()
    findings = fields.Text()

    @api.depends('planned_date', 'completed_date', 'frequency_days', 'state')
    def _compute_next_due(self):
        for rec in self:
            base = rec.completed_date or rec.planned_date
            rec.next_due_date = fields.Date.add(base, days=rec.frequency_days) if base and rec.frequency_days > 0 else base

    @api.constrains('frequency_days', 'cost')
    def _check_values(self):
        for rec in self:
            if rec.frequency_days <= 0:
                raise ValidationError(_('Maintenance frequency must be greater than zero.'))
            if rec.cost < 0:
                raise ValidationError(_('Maintenance cost cannot be negative.'))

    def action_start(self):
        self.write({'state': 'in_progress'})
        self.mapped('equipment_id').action_set_maintenance()

    def action_done(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.write({
                'state': 'done',
                'completed_date': today,
                'performed_by': rec.performed_by.id if rec.performed_by else self.env.user.id,
            })
            if rec.equipment_id.status == 'maintenance':
                rec.equipment_id.action_set_available()

    def action_cancel(self):
        self.write({'state': 'cancelled'})
