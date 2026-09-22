from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestQualityChecklist(models.Model):
    _name = 'pest.quality.checklist'
    _description = 'PestOps Quality Checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'procedure_id, version desc, id desc'

    name = fields.Char(required=True, tracking=True)
    procedure_id = fields.Many2one('pest.quality.procedure', required=True, ondelete='cascade', tracking=True)
    version = fields.Char(required=True, default='1.0', tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    description = fields.Text()
    site_ids = fields.Many2many('pest.site', string='Restricted Sites')
    item_ids = fields.One2many('pest.quality.checklist.item', 'checklist_id', string='Checklist Items', copy=True)
    check_ids = fields.One2many('pest.quality.check', 'checklist_id')
    item_count = fields.Integer(compute='_compute_counts')
    check_count = fields.Integer(compute='_compute_counts')
    company_id = fields.Many2one(related='procedure_id.company_id', store=True, index=True)

    _uniq_version = models.Constraint(
        'UNIQUE(procedure_id, version)',
        'Checklist version must be unique per procedure.',
    )

    @api.depends('item_ids', 'check_ids')
    def _compute_counts(self):
        for record in self:
            record.item_count = len(record.item_ids)
            record.check_count = len(record.check_ids)

    @api.constrains('item_ids')
    def _check_items(self):
        for record in self:
            if not record.item_ids:
                continue
            orders = record.item_ids.mapped('sequence')
            if len(orders) != len(set(orders)):
                raise ValidationError(_('Checklist item sequence must be unique within a checklist.'))

    def action_new_version(self):
        self.ensure_one()
        version = self.version or '1.0'
        try:
            major, minor = version.split('.', 1)
            new_version = f'{int(major)}.{int(minor) + 1}'
        except (ValueError, TypeError):
            new_version = version + '.1'
        copy = self.copy({'version': new_version, 'name': f'{self.name} v{new_version}', 'active': True})
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Checklist Version'),
            'res_model': 'pest.quality.checklist',
            'view_mode': 'form',
            'res_id': copy.id,
        }


class PestQualityChecklistItem(models.Model):
    _name = 'pest.quality.checklist.item'
    _description = 'PestOps Quality Checklist Item'
    _order = 'sequence, id'

    checklist_id = fields.Many2one('pest.quality.checklist', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    question = fields.Text(required=True)
    response_type = fields.Selection([
        ('pass_fail', 'Pass / Fail'),
        ('yes_no', 'Yes / No'),
        ('text', 'Text'),
        ('number', 'Number'),
    ], default='pass_fail', required=True)
    mandatory = fields.Boolean(default=True)
    guidance = fields.Text()
    expected_value = fields.Char()
    failure_severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(related='checklist_id.company_id', store=True, index=True)


class PestQualityCheck(models.Model):
    _name = 'pest.quality.check'
    _description = 'PestOps Quality Check'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('pest.quality.check'), readonly=True, copy=False)
    visit_id = fields.Many2one('pest.visit', required=True, ondelete='cascade', tracking=True)
    site_id = fields.Many2one(related='visit_id.site_id', store=True, index=True)
    company_id = fields.Many2one(related='visit_id.company_id', store=True, index=True)
    technician_id = fields.Many2one('res.users', related='visit_id.technician_id', store=True)
    procedure_id = fields.Many2one('pest.quality.procedure', required=True, ondelete='restrict', tracking=True)
    checklist_id = fields.Many2one('pest.quality.checklist', required=True, ondelete='restrict', tracking=True)
    date = fields.Datetime(default=fields.Datetime.now, required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', required=True, tracking=True)
    result = fields.Selection([
        ('compliant', 'Compliant'),
        ('partial', 'Partially Compliant'),
        ('non_compliant', 'Non-Compliant'),
    ], tracking=True)
    notes = fields.Text()
    line_ids = fields.One2many('pest.quality.check.line', 'check_id', string='Checklist Responses', copy=True)
    nonconformity_ids = fields.One2many('pest.quality.nonconformity', 'check_id')
    line_count = fields.Integer(compute='_compute_counts')
    failed_count = fields.Integer(compute='_compute_counts')
    nonconformity_count = fields.Integer(compute='_compute_counts')
    open_nonconformity_count = fields.Integer(compute='_compute_counts', store=True)

    @api.depends('line_ids', 'line_ids.passed', 'nonconformity_ids', 'nonconformity_ids.state')
    def _compute_counts(self):
        for record in self:
            record.line_count = len(record.line_ids)
            record.failed_count = len(record.line_ids.filtered(lambda l: l.passed is False))
            record.nonconformity_count = len(record.nonconformity_ids)
            record.open_nonconformity_count = len(record.nonconformity_ids.filtered(lambda n: n.state in ('open', 'in_progress')))

    @api.constrains('procedure_id', 'checklist_id', 'site_id')
    def _check_checklist_consistency(self):
        for record in self:
            if record.checklist_id and record.procedure_id and record.checklist_id.procedure_id != record.procedure_id:
                raise ValidationError(_('The selected checklist must belong to the selected procedure.'))
            if record.checklist_id and record.checklist_id.site_ids and record.site_id not in record.checklist_id.site_ids:
                raise ValidationError(_('This checklist is restricted to specific sites and cannot be used for this visit site.'))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.checklist_id:
                record._load_checklist_lines()
        return records

    def write(self, vals):
        result = super().write(vals)
        if 'checklist_id' in vals:
            for record in self:
                if not record.line_ids and record.checklist_id:
                    record._load_checklist_lines()
        return result

    def _load_checklist_lines(self):
        self.ensure_one()
        if self.line_ids:
            return
        lines = []
        for item in self.checklist_id.item_ids.filtered('active').sorted('sequence'):
            lines.append({
                'check_id': self.id,
                'item_id': item.id,
                'sequence': item.sequence,
                'name': item.name,
                'question': item.question,
                'response_type': item.response_type,
                'mandatory': item.mandatory,
                'guidance': item.guidance,
                'expected_value': item.expected_value,
                'failure_severity': item.failure_severity,
            })
        if lines:
            self.env['pest.quality.check.line'].create(lines)

    def action_start(self):
        for record in self:
            if record.state == 'draft':
                record.write({'state': 'in_progress'})

    def _line_passed(self, line):
        if line.response_type == 'pass_fail':
            return {'pass': True, 'fail': False, 'na': True}.get(line.response)
        if line.response_type == 'yes_no':
            return {'yes': True, 'no': False, 'na': True}.get(line.response)
        if line.response_type == 'number':
            if line.numeric_value is None:
                return None
            if line.expected_value:
                try:
                    return line.numeric_value == float(line.expected_value)
                except ValueError:
                    return True
            return True
        if line.response_type == 'text':
            return bool(line.text_value)
        return None

    def action_complete(self):
        for record in self:
            if not record.line_ids:
                raise UserError(_('This quality check has no checklist response lines.'))
            for line in record.line_ids:
                if line.mandatory and not line.has_response:
                    raise UserError(_('Mandatory checklist item is not answered: %s') % line.question)
                line.passed = record._line_passed(line)
            record._create_nonconformities_from_failed_lines()
            failed = record.line_ids.filtered(lambda l: l.passed is False)
            result = 'non_compliant' if failed else 'compliant'
            if failed and len(failed) < len(record.line_ids):
                result = 'partial'
            record.write({'state': 'done', 'result': result})

    def _create_nonconformities_from_failed_lines(self):
        NC = self.env['pest.quality.nonconformity']
        for line in self.line_ids.filtered(lambda l: l.passed is False):
            existing = NC.search([
                ('check_line_id', '=', line.id),
                ('state', '!=', 'cancelled'),
            ], limit=1)
            if existing:
                continue
            NC.create({
                'check_id': self.id,
                'check_line_id': line.id,
                'severity': line.failure_severity,
                'description': line.notes or line.question,
                'corrective_action': line.guidance,
                'responsible_user_id': self.visit_id.technician_id.id,
                'due_date': fields.Date.context_today(self) if line.failure_severity in ('high', 'critical') else False,
            })

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_view_nonconformities(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Non-Conformities'),
            'res_model': 'pest.quality.nonconformity',
            'view_mode': 'list,form',
            'domain': [('check_id', '=', self.id)],
        }


class PestQualityCheckLine(models.Model):
    _name = 'pest.quality.check.line'
    _description = 'PestOps Quality Check Line'
    _order = 'sequence, id'

    check_id = fields.Many2one('pest.quality.check', required=True, ondelete='cascade')
    item_id = fields.Many2one('pest.quality.checklist.item', ondelete='set null')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    question = fields.Text(required=True)
    response_type = fields.Selection([
        ('pass_fail', 'Pass / Fail'),
        ('yes_no', 'Yes / No'),
        ('text', 'Text'),
        ('number', 'Number'),
    ], required=True)
    mandatory = fields.Boolean(default=True)
    guidance = fields.Text()
    expected_value = fields.Char()
    failure_severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium', required=True)
    response = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('yes', 'Yes'),
        ('no', 'No'),
        ('na', 'N/A'),
    ])
    text_value = fields.Text()
    numeric_value = fields.Float()
    has_response = fields.Boolean(compute='_compute_response_state')
    passed = fields.Boolean(compute='_compute_passed', store=True)
    notes = fields.Text()
    nonconformity_ids = fields.One2many('pest.quality.nonconformity', 'check_line_id')

    @api.depends('response', 'text_value', 'numeric_value', 'response_type')
    def _compute_response_state(self):
        for line in self:
            if line.response_type in ('pass_fail', 'yes_no'):
                line.has_response = bool(line.response)
            elif line.response_type == 'text':
                line.has_response = bool(line.text_value)
            else:
                line.has_response = line.numeric_value is not None

    @api.depends('response', 'text_value', 'numeric_value', 'response_type', 'expected_value')
    def _compute_passed(self):
        for line in self:
            passed = True
            if line.response_type == 'pass_fail':
                passed = {'pass': True, 'fail': False, 'na': True}.get(line.response, False if line.has_response else True)
            elif line.response_type == 'yes_no':
                passed = {'yes': True, 'no': False, 'na': True}.get(line.response, False if line.has_response else True)
            elif line.response_type == 'text':
                passed = bool(line.text_value) if line.has_response else True
            elif line.response_type == 'number':
                if not line.has_response:
                    passed = True
                elif line.expected_value:
                    try:
                        passed = line.numeric_value == float(line.expected_value)
                    except ValueError:
                        passed = True
            line.passed = passed
