from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PestQualityProcedure(models.Model):
    _name = 'pest.quality.procedure'
    _description = 'PestOps Quality Procedure'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name, id'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, copy=False, tracking=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True, tracking=True)
    version = fields.Char(default='1.0', required=True, tracking=True)
    owner_id = fields.Many2one('res.users', default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True, index=True)
    scope = fields.Selection([
        ('field', 'Field Operations'),
        ('warehouse', 'Warehouse / Stock'),
        ('equipment', 'Equipment'),
        ('customer_service', 'Customer Service'),
        ('general', 'General'),
    ], default='field', required=True, tracking=True)
    purpose = fields.Text()
    instructions = fields.Html()
    checklist_ids = fields.One2many('pest.quality.checklist', 'procedure_id', string='Checklists')
    checklist_count = fields.Integer(compute='_compute_counts')
    check_count = fields.Integer(compute='_compute_counts')
    current_checklist_id = fields.Many2one('pest.quality.checklist', compute='_compute_current_checklist')

    _code_company_uniq = models.Constraint(
        'UNIQUE(company_id, code)',
        'Procedure code must be unique per company.',
    )

    @api.depends('checklist_ids', 'checklist_ids.check_ids')
    def _compute_counts(self):
        for record in self:
            record.checklist_count = len(record.checklist_ids)
            record.check_count = sum(len(c.check_ids) for c in record.checklist_ids)

    @api.depends('checklist_ids', 'checklist_ids.active', 'checklist_ids.version')
    def _compute_current_checklist(self):
        for record in self:
            active = record.checklist_ids.filtered('active').sorted(lambda c: (c.version, c.id), reverse=True)
            record.current_checklist_id = active[:1] if active else False

    @api.constrains('version')
    def _check_version(self):
        for record in self:
            if not record.version.strip():
                raise ValidationError(_('Procedure version cannot be empty.'))
