# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EduflowTeacher(models.Model):
    _name = 'eduflow.teacher'
    _description = "Teacher"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    matricule = fields.Char(string="Registration Number", copy=False, readonly=True,
                             default=lambda self: 'New')
    name = fields.Char(string="Full Name", required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employee Record (HR)",
                                   help="Optional link to Odoo HR module (now directly in eduflow, parents remain res.partner).")
    user_id = fields.Many2one('res.users', string="Related User",
                               help="Used for teacher portal.")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    specialty = fields.Char(string="Specialty")
    subject_ids = fields.Many2many('eduflow.subject', string="Subjects Taught")
    classroom_ids = fields.One2many('eduflow.classroom', 'principal_teacher_id',
                                     string="Homeroom Classes")
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string="Status", default='active')
    timetable_ids = fields.One2many('eduflow.timetable.session', 'teacher_id',
                                     string="Timetable")
    availability_ids = fields.One2many('eduflow.teacher.availability', 'teacher_id', string="Availabilities")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('matricule', 'New') == 'New':
                vals['matricule'] = self.env['ir.sequence'].next_by_code(
                    'eduflow.teacher') or 'New'
        return super().create(vals_list)
