from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PestEquipment(models.Model):
    _name = 'pest.equipment'
    _description = 'PestOps Equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc, id asc'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.equipment'),
        readonly=True,
        copy=False,
        tracking=True,
    )
    equipment_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('vehicle', 'Vehicle'),
        ('ppe', 'PPE'),
        ('device', 'Monitoring Device'),
        ('other', 'Other'),
    ], default='equipment', required=True, tracking=True)
    product_id = fields.Many2one(
        'product.product',
        string='Stock Product',
        help='Optional product reference for the non-consumable asset.',
    )
    serial_number = fields.Char(index=True, tracking=True)
    asset_tag = fields.Char(index=True, tracking=True)
    registration_number = fields.Char(string='Registration / Plate', tracking=True)
    manufacturer = fields.Char()
    model_name = fields.Char(string='Model')
    purchase_date = fields.Date()
    warranty_end_date = fields.Date()
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsible',
        tracking=True,
    )
    assigned_user_id = fields.Many2one(
        'res.users',
        string='Current Technician',
        tracking=True,
        readonly=True,
    )
    assigned_site_id = fields.Many2one(
        'pest.site',
        string='Current Site',
        tracking=True,
        readonly=True,
    )
    status = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'In Maintenance'),
        ('out_of_service', 'Out of Service'),
        ('retired', 'Retired'),
    ], default='available', required=True, tracking=True)
    active = fields.Boolean(default=True)
    notes = fields.Html()

    assignment_ids = fields.One2many('pest.equipment.assignment', 'equipment_id')
    inspection_ids = fields.One2many('pest.equipment.inspection', 'equipment_id')
    maintenance_ids = fields.One2many('pest.equipment.maintenance', 'equipment_id')
    usage_ids = fields.One2many('pest.equipment.usage', 'equipment_id')

    assignment_count = fields.Integer(compute='_compute_counts')
    inspection_count = fields.Integer(compute='_compute_counts')
    maintenance_count = fields.Integer(compute='_compute_counts')
    usage_count = fields.Integer(compute='_compute_counts')
    next_inspection_date = fields.Date(compute='_compute_due_dates', store=True)
    next_maintenance_date = fields.Date(compute='_compute_due_dates', store=True)
    has_due_action = fields.Boolean(compute='_compute_due_dates', store=True)

    @api.depends('assignment_ids', 'inspection_ids', 'maintenance_ids', 'usage_ids')
    def _compute_counts(self):
        for equipment in self:
            equipment.assignment_count = len(equipment.assignment_ids)
            equipment.inspection_count = len(equipment.inspection_ids)
            equipment.maintenance_count = len(equipment.maintenance_ids)
            equipment.usage_count = len(equipment.usage_ids)

    @api.depends(
        'inspection_ids.next_due_date', 'inspection_ids.state',
        'maintenance_ids.next_due_date', 'maintenance_ids.state',
    )
    def _compute_due_dates(self):
        today = fields.Date.context_today(self)
        for equipment in self:
            inspections = equipment.inspection_ids.filtered(
                lambda x: x.state == 'open' and x.next_due_date
            )
            maintenances = equipment.maintenance_ids.filtered(
                lambda x: x.state not in ('cancelled', 'done') and x.next_due_date
            )
            insp_dates = inspections.mapped('next_due_date')
            maint_dates = maintenances.mapped('next_due_date')
            equipment.next_inspection_date = min(insp_dates) if insp_dates else False
            equipment.next_maintenance_date = min(maint_dates) if maint_dates else False
            equipment.has_due_action = any(
                d and d <= today for d in (equipment.next_inspection_date, equipment.next_maintenance_date)
            )

    @api.constrains('serial_number', 'company_id')
    def _check_serial_unique(self):
        for record in self.filtered('serial_number'):
            duplicate = self.search([
                ('id', '!=', record.id),
                ('serial_number', '=', record.serial_number),
                ('company_id', '=', record.company_id.id),
                ('active', '=', True),
            ], limit=1)
            if duplicate:
                raise ValidationError(_('Serial number must be unique per company.'))

    def action_set_maintenance(self):
        self.write({'status': 'maintenance'})

    def action_set_available(self):
        self.write({'status': 'available'})

    def action_set_out_of_service(self):
        self.write({'status': 'out_of_service'})

    def action_retire(self):
        self.write({'status': 'retired', 'active': False, 'assigned_user_id': False, 'assigned_site_id': False})

    def action_view_assignments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assignments'),
            'res_model': 'pest.equipment.assignment',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
        }

    def action_view_inspections(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inspections'),
            'res_model': 'pest.equipment.inspection',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
        }

    def action_view_maintenance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Maintenance'),
            'res_model': 'pest.equipment.maintenance',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
        }

    def action_view_usage(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Visit Usage'),
            'res_model': 'pest.equipment.usage',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
        }

    @api.model
    def _cron_due_actions(self):
        today = fields.Date.context_today(self)
        equipment = self.search([('active', '=', True)])
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return True
        for item in equipment:
            if item.next_inspection_date and item.next_inspection_date <= today:
                existing = self.env['mail.activity'].search_count([
                    ('res_model', '=', self._name),
                    ('res_id', '=', item.id),
                    ('summary', '=', 'PestOps Equipment Inspection Due'),
                ])
                if not existing:
                    self.env['mail.activity'].create({
                        'activity_type_id': activity_type.id,
                        'res_model_id': self.env['ir.model']._get_id(self._name),
                        'res_id': item.id,
                        'user_id': (item.responsible_id or self.env.user).id,
                        'summary': 'PestOps Equipment Inspection Due',
                        'note': _('Inspection is due for %s.') % item.display_name,
                        'date_deadline': today,
                    })
            if item.next_maintenance_date and item.next_maintenance_date <= today:
                existing = self.env['mail.activity'].search_count([
                    ('res_model', '=', self._name),
                    ('res_id', '=', item.id),
                    ('summary', '=', 'PestOps Equipment Maintenance Due'),
                ])
                if not existing:
                    self.env['mail.activity'].create({
                        'activity_type_id': activity_type.id,
                        'res_model_id': self.env['ir.model']._get_id(self._name),
                        'res_id': item.id,
                        'user_id': (item.responsible_id or self.env.user).id,
                        'summary': 'PestOps Equipment Maintenance Due',
                        'note': _('Maintenance is due for %s.') % item.display_name,
                        'date_deadline': today,
                    })
        return True
