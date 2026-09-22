from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestEquipmentAssignment(models.Model):
    _name = 'pest.equipment.assignment'
    _description = 'PestOps Equipment Assignment'
    _inherit = ['mail.thread']
    _order = 'date_start desc, id desc'

    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.equipment.assignment'),
        readonly=True,
        copy=False,
    )
    equipment_id = fields.Many2one('pest.equipment', required=True, ondelete='cascade', tracking=True)
    user_id = fields.Many2one('res.users', string='Technician', required=True, tracking=True)
    site_id = fields.Many2one('pest.site', string='Site', tracking=True)
    date_start = fields.Datetime(required=True, default=fields.Datetime.now, tracking=True)
    date_end = fields.Datetime(tracking=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], default='active', required=True, tracking=True)
    notes = fields.Text()

    def _sync_equipment_assignment(self):
        for rec in self:
            if rec.state == 'active':
                rec.equipment_id.write({
                    'assigned_user_id': rec.user_id.id,
                    'assigned_site_id': rec.site_id.id if rec.site_id else False,
                    'status': 'assigned',
                })
            elif rec.equipment_id.assigned_user_id.id == rec.user_id.id:
                rec.equipment_id.write({
                    'assigned_user_id': False,
                    'assigned_site_id': False,
                    'status': 'available' if rec.equipment_id.status == 'assigned' else rec.equipment_id.status,
                })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        active_records = records.filtered(lambda r: r.state == 'active')
        for rec in active_records:
            rec._validate_activation()
        active_records._sync_equipment_assignment()
        return records

    def write(self, vals):
        result = super().write(vals)
        if any(key in vals for key in ('state', 'equipment_id', 'user_id', 'site_id')):
            for rec in self:
                if rec.state == 'active':
                    rec._validate_activation()
                rec._sync_equipment_assignment()
        return result

    def _validate_activation(self):
        self.ensure_one()
        if self.equipment_id.status in ('maintenance', 'out_of_service', 'retired'):
            raise UserError(_('This equipment is not available for assignment.'))
        active = self.search([
            ('id', '!=', self.id),
            ('equipment_id', '=', self.equipment_id.id),
            ('state', '=', 'active'),
        ], limit=1)
        if active:
            raise UserError(_('This equipment is already assigned to %s.') % active.user_id.display_name)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError(_('Assignment end must be after assignment start.'))

    @api.constrains('equipment_id', 'state')
    def _check_active_assignment(self):
        for rec in self.filtered(lambda r: r.state == 'active'):
            duplicate = self.search([
                ('id', '!=', rec.id),
                ('equipment_id', '=', rec.equipment_id.id),
                ('state', '=', 'active'),
            ], limit=1)
            if duplicate:
                raise ValidationError(_('An equipment can have only one active assignment.'))

    def action_activate(self):
        for rec in self:
            if rec.state == 'active':
                rec._validate_activation()
                rec._sync_equipment_assignment()
                continue
            rec._validate_activation()
            super(PestEquipmentAssignment, rec).write({
                'state': 'active',
                'date_end': False,
            })
            rec._sync_equipment_assignment()

    def action_close(self):
        for rec in self:
            if rec.state != 'active':
                continue
            super(PestEquipmentAssignment, rec).write({
                'state': 'closed',
                'date_end': rec.date_end or fields.Datetime.now(),
            })
            rec._sync_equipment_assignment()

    def action_cancel(self):
        for rec in self:
            if rec.state == 'closed':
                raise UserError(_('A closed assignment cannot be cancelled.'))
            super(PestEquipmentAssignment, rec).write({
                'state': 'cancelled',
                'date_end': rec.date_end or fields.Datetime.now(),
            })
            rec._sync_equipment_assignment()
