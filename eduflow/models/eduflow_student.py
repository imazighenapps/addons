# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EduflowStudent(models.Model):
    _name = 'eduflow.student'
    _description = "Student"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _rec_names_search = ['name', 'matricule']

    matricule = fields.Char(string="Registration Number", copy=False, readonly=True,
                             default=lambda self: 'New')
    name = fields.Char(string="Nom", required=True, tracking=True)
    firstname = fields.Char(string="First Name", required=True, tracking=True)
    display_name = fields.Char(compute='_compute_display_name', store=True)
    birth_date = fields.Date(string="Birth Date")
    birth_place = fields.Char(string="Birth Place")
    gender = fields.Selection([
        ('m', 'Male'), ('f', 'Female'),
    ], string="Sexe")
    nationality_id = fields.Many2one('res.country', string="Nationality")
    address = fields.Char(string="Address")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    photo = fields.Image(string="Photo", max_width=512, max_height=512)
    id_document_number = fields.Char(string="ID Document No.")
    medical_info = fields.Text(string="Authorized Medical Information")
    admin_notes = fields.Text(string="Informations administratives")

    status = fields.Selection([
        ('prospect', 'Prospect'),
        ('candidate', 'Applicant'),
        ('waiting', 'Pending Enrollment'),
        ('enrolled', 'Enrolled'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('transferred', 'Transferred'),
        ('graduated', 'Graduated'),
        ('left', 'Left'),
    ], string="Status", default='prospect', required=True, tracking=True)

    parent_rel_ids = fields.One2many('eduflow.student.parent.rel', 'student_id',
                                      string="Guardians")
    admission_ids = fields.One2many('eduflow.admission', 'student_id', string="Admissions")
    enrollment_ids = fields.One2many('eduflow.enrollment', 'student_id', string="Enrollments")
    current_enrollment_id = fields.Many2one('eduflow.enrollment', string="Enrollment active",
                                             compute='_compute_current_enrollment', store=True)
    current_classroom_id = fields.Many2one('eduflow.classroom', string="Current Class",
                                            related='current_enrollment_id.classroom_id', store=True)
    attendance_ids = fields.One2many('eduflow.attendance', 'student_id', string="Attendance Records")
    grade_ids = fields.One2many('eduflow.grade', 'student_id', string="Grades")
    fee_ids = fields.One2many('eduflow.fee', 'student_id', string="Fees")
    document_ids = fields.Many2many('ir.attachment', string="Documents")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    @api.depends('name', 'firstname', 'matricule')
    def _compute_display_name(self):
        for rec in self:
            full_name = f"{rec.firstname or ''} {rec.name or ''}".strip()
            rec.display_name = f"[{rec.matricule}] {full_name}" if rec.matricule else full_name

    @api.depends('enrollment_ids.state', 'enrollment_ids.year_id.active_year')
    def _compute_current_enrollment(self):
        for rec in self:
            active = rec.enrollment_ids.filtered(
                lambda e: e.year_id.active_year and e.state in ('confirmed', 'active'))
            rec.current_enrollment_id = active[:1]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('matricule', 'New') == 'New':
                vals['matricule'] = self.env['ir.sequence'].next_by_code(
                    'eduflow.student.matricule') or 'New'
        return super().create(vals_list)
