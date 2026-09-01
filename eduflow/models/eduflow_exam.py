# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class EduflowExam(models.Model):
    _name = 'eduflow.exam'
    _description = "Exam / Assessment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string="Nom", required=True, tracking=True)
    exam_type = fields.Selection([
        ('continuous', 'Continuous Assessment'),
        ('supervised', 'Supervised Test'),
        ('trimester', 'Trimester Exam'),
        ('semester', 'Semester Exam'),
        ('final', 'Final Exam'),
    ], string="Type", default='continuous', required=True)
    year_id = fields.Many2one('eduflow.academic.year', string="Academic Year", required=True)
    period_id = fields.Many2one('eduflow.academic.period', string="Period", required=True)
    classroom_id = fields.Many2one('eduflow.classroom', string="Class", required=True)
    subject_id = fields.Many2one('eduflow.subject', string="Subject", required=True)
    date = fields.Date(string="Date")
    teacher_id = fields.Many2one('eduflow.teacher', string="Teacher")
    coefficient = fields.Float(string="Coefficient", default=1.0)
    duration = fields.Float(string="Duration (hours)")
    grade_ids = fields.One2many('eduflow.grade', 'exam_id', string="Grades")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('grading', 'Grade Entry'),
        ('validated', 'Validated'),
    ], string="Status", default='draft', tracking=True)
    company_id = fields.Many2one('res.company', string="Institution",
                                  related='classroom_id.company_id', store=True, readonly=True)

    def action_open_grading(self):
        self.write({'state': 'grading'})

    def action_validate(self):
        self.write({'state': 'validated'})

    def action_set_draft(self):
        self.write({'state': 'draft'})

    def action_generate_grade_grid(self):
        """F2.2 -- pre-fill grade_ids with one line per student currently
        enrolled in the exam's class, so the teacher only has to fill in
        the 'grade' column of the embedded list instead of creating each
        eduflow.grade one at a time."""
        self.ensure_one()
        existing_students = self.grade_ids.mapped('student_id')
        enrollments = self.env['eduflow.enrollment'].search([
            ('classroom_id', '=', self.classroom_id.id),
            ('state', 'in', ('confirmed', 'active')),
        ])
        missing_students = enrollments.mapped('student_id') - existing_students
        Grade = self.env['eduflow.grade']
        for student in missing_students:
            Grade.create({
                'exam_id': self.id,
                'student_id': student.id,
                'grade': 0.0,
            })
        if self.state == 'draft':
            self.state = 'grading'
        return True
