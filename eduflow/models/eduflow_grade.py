# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class EduflowGrade(models.Model):
    _name = 'eduflow.grade'
    _description = "Grade"
    _inherit = ['mail.thread']
    _order = 'exam_id, student_id'

    exam_id = fields.Many2one('eduflow.exam', string="Examen", required=True, ondelete='cascade')
    student_id = fields.Many2one('eduflow.student', string="Student", required=True)
    subject_id = fields.Many2one(related='exam_id.subject_id', string="Subject", store=True)
    grade = fields.Float(string="Grade (/20)", tracking=True)
    appreciation = fields.Char(string="Comment")
    company_id = fields.Many2one('res.company', string="Institution",
                                  related='exam_id.company_id', store=True, readonly=True)

    _sql_constraints = [
        ('exam_student_uniq', 'unique(exam_id, student_id)',
         "A grade already exists for this student on this exam."),
    ]

    @api.constrains('grade')
    def _check_grade_range(self):
        for rec in self:
            if rec.grade < 0 or rec.grade > 20:
                raise ValidationError(_("Grade must be between 0 and 20."))

    def _eduflow_can_bypass_grade_lock(self):
        return (self.env.user.has_group('eduflow.group_eduflow_admin')
                or self.env.user.has_group('eduflow.group_eduflow_direction')
                or self.env.user.has_group('eduflow.group_eduflow_administration'))

    def write(self, vals):
        # F2.2 -- once the exam is validated, teachers can no longer edit
        # grades; Management/Administration/Admin keep full rights.
        if 'grade' in vals or 'appreciation' in vals:
            if not self._eduflow_can_bypass_grade_lock():
                locked = self.filtered(lambda g: g.exam_id.state == 'validated')
                if locked:
                    raise UserError(_(
                        "Grades of a validated exam can no longer be edited by "
                        "teachers. Please contact the school administration."))
        return super().write(vals)
