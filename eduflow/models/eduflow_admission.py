# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EduflowAdmission(models.Model):
    _name = 'eduflow.admission'
    _description = "Admission Application"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string="File No.", copy=False, readonly=True,
                        default=lambda self: 'New')
    student_id = fields.Many2one('eduflow.student', string="Applicant", required=True,
                                  tracking=True)
    level_id = fields.Many2one('eduflow.level', string="Requested Level", required=True)
    year_id = fields.Many2one('eduflow.academic.year', string="Academic Year", required=True,
                               default=lambda self: self.env['eduflow.academic.year'].search(
                                   [('active_year', '=', True)], limit=1))
    parent_id = fields.Many2one('eduflow.parent', string="Guardian")
    request_date = fields.Date(string="Application Date", default=fields.Date.context_today)
    document_ids = fields.Many2many('ir.attachment', string="Documents")
    notes = fields.Text(string="Observations")
    interview_date = fields.Datetime(string="Interview / Test Date")
    interview_result = fields.Text(string="Interview / Test Result")

    state = fields.Selection([
        ('new', 'New Application'),
        ('review', 'Under Review'),
        ('interview', 'Interview / Test'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
        ('enrolled', 'Enrolled'),
    ], string="Status", default='new', required=True, tracking=True)

    # F3.3 -- required document tracking
    document_line_ids = fields.One2many('eduflow.admission.document.line', 'admission_id',
                                         string="Required Documents")
    documents_complete = fields.Boolean(string="Documents Complete",
                                         compute='_compute_documents_complete', store=True)
    company_id = fields.Many2one('res.company', string="Institution",
                                  default=lambda self: self.env.company)

    @api.depends('document_line_ids.received', 'document_line_ids.required')
    def _compute_documents_complete(self):
        for rec in self:
            required_lines = rec.document_line_ids.filtered('required')
            rec.documents_complete = all(line.received for line in required_lines)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'eduflow.admission') or 'New'
        records = super().create(vals_list)
        records._populate_document_lines()
        return records

    def _populate_document_lines(self):
        """Pre-fill document_line_ids from eduflow.document.type entries
        matching the requested level (or generic, level-less entries)."""
        DocType = self.env['eduflow.document.type']
        for rec in self:
            if rec.document_line_ids:
                continue
            doc_types = DocType.search(['|', ('level_id', '=', False),
                                         ('level_id', '=', rec.level_id.id)])
            rec.document_line_ids = [(0, 0, {
                'document_type_id': dt.id,
                'required': dt.required,
            }) for dt in doc_types]

    @api.model
    def create_from_public_form(self, values):
        """F3.1 -- entry point used by the public (auth='public') pre-
        registration controller. `values` is expected to already have been
        validated/sanitized server-side by the controller; this method only
        performs the business creation (student as 'prospect', parent if
        needed, admission at state 'new') under sudo(), since anonymous
        visitors have no direct write access to these models."""
        self = self.sudo()
        Student = self.env['eduflow.student'].sudo()
        Parent = self.env['eduflow.parent'].sudo()

        # F3.1 fix (audit 2026-08-31): never reuse an existing parent from an
        # anonymous public form — always create a fresh candidate parent.
        # Deduplication is left to the back-office via manual merge.
        parent = False
        if values.get('parent_name') or values.get('parent_email'):
            parent = Parent.create({
                'name': values.get('parent_name') or values.get('parent_email'),
                'email': values.get('parent_email'),
                'phone': values.get('parent_phone'),
            })

        student = Student.create({
            'name': values.get('student_name'),
            'firstname': values.get('student_firstname'),
            'birth_date': values.get('student_birth_date') or False,
            'status': 'prospect',
        })
        if parent:
            self.env['eduflow.student.parent.rel'].sudo().create({
                'student_id': student.id,
                'parent_id': parent.id,
                'relation': values.get('parent_relation', 'guardian'),
                'is_primary': True,
                'is_financial': True,
            })

        admission = self.create({
            'student_id': student.id,
            'level_id': values.get('level_id'),
            'parent_id': parent.id if parent else False,
            'notes': values.get('notes'),
        })
        return admission

    def action_start_review(self):
        self.write({'state': 'review'})

    def action_schedule_interview(self):
        self.write({'state': 'interview'})

    def action_accept(self):
        enforce = self.env['ir.config_parameter'].sudo().get_param(
            'eduflow.require_complete_documents', 'False') == 'True'
        if enforce:
            incomplete = self.filtered(lambda a: not a.documents_complete)
            if incomplete:
                raise UserError(_(
                    "The following admission files still have missing required "
                    "documents and cannot be accepted yet: %s")
                    % ', '.join(incomplete.mapped('display_name')))
        self.write({'state': 'accepted'})
        self.student_id.write({'status': 'waiting'})

    def action_refuse(self):
        self.write({'state': 'refused'})

    def action_set_new(self):
        self.write({'state': 'new'})

    def action_create_enrollment(self):
        self.ensure_one()
        enrollment = self.env['eduflow.enrollment'].create({
            'student_id': self.student_id.id,
            'year_id': self.year_id.id,
            'level_id': self.level_id.id,
            'admission_id': self.id,
        })
        self.write({'state': 'enrolled'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eduflow.enrollment',
            'view_mode': 'form',
            'res_id': enrollment.id,
        }
