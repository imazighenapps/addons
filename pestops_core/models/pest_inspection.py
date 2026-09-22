from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PestInspection(models.Model):
    _name = 'pest.inspection'
    _description = 'Pest Inspection'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('pest.inspection'),
        readonly=True,
        copy=False,
    )
    visit_id = fields.Many2one(
        'pest.visit',
        required=True,
        ondelete='cascade',
        index=True,
    )
    site_id = fields.Many2one(
        related='visit_id.site_id',
        store=True,
        index=True,
    )
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    technician_id = fields.Many2one(
        related='visit_id.technician_id',
        store=True,
    )
    activity_level = fields.Selection(
        [
            ('none', 'None'),
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='none',
        required=True,
    )
    notes = fields.Text()
    image_1920 = fields.Image()
    line_ids = fields.One2many(
        'pest.inspection.line',
        'inspection_id',
        copy=True,
    )
    action_required_count = fields.Integer(compute='_compute_action_counts')
    critical_count = fields.Integer(compute='_compute_action_counts')

    @api.depends('line_ids.action_required', 'line_ids.activity_level')
    def _compute_action_counts(self):
        for inspection in self:
            inspection.action_required_count = len(inspection.line_ids.filtered('action_required'))
            inspection.critical_count = len(inspection.line_ids.filtered(lambda l: l.activity_level == 'critical'))


class PestInspectionLine(models.Model):
    _name = 'pest.inspection.line'
    _description = 'Pest Inspection Line'

    inspection_id = fields.Many2one(
        'pest.inspection',
        required=True,
        ondelete='cascade',
    )
    control_point_id = fields.Many2one(
        'pest.control.point',
        required=True,
        ondelete='restrict',
    )
    pest_id = fields.Many2one('pest.type', ondelete='restrict')
    activity_level = fields.Selection(
        [
            ('none', 'None'),
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='none',
        required=True,
    )
    evidence = fields.Selection(
        [
            ('none', 'None'),
            ('live_pest', 'Live Pest'),
            ('droppings', 'Droppings'),
            ('damage', 'Damage'),
            ('nest', 'Nest'),
            ('odor', 'Odor'),
            ('trap_activity', 'Trap Activity'),
            ('other', 'Other'),
        ],
        default='none',
    )
    action_required = fields.Boolean()
    observation = fields.Text()
    recommended_action = fields.Text()
    image_1920 = fields.Image()
    anomaly_ids = fields.One2many('pest.anomaly', 'inspection_line_id')
