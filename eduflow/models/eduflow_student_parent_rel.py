# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EduflowStudentParentRel(models.Model):
    _name = 'eduflow.student.parent.rel'
    _description = "Student - Guardian Link"
    _rec_name = 'parent_id'

    student_id = fields.Many2one('eduflow.student', string="Student",
                                  required=True, ondelete='cascade')
    parent_id = fields.Many2one('eduflow.parent', string="Guardian",
                                 required=True, ondelete='cascade')
    relation = fields.Selection([
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
        ('other', 'Other Guardian'),
    ], string="Lien", required=True, default='father')
    is_primary = fields.Boolean(string="Primary Guardian")
    is_financial = fields.Boolean(string="Guardian financier")
    can_communicate = fields.Boolean(string="Allowed to receive communications",
                                      default=True)

    _sql_constraints = [
        ('student_parent_uniq', 'unique(student_id, parent_id)',
         "This guardian is already linked to this student."),
    ]

    @api.constrains('is_primary', 'student_id')
    def _check_single_primary(self):
        for rec in self:
            if rec.is_primary:
                other = self.search([
                    ('student_id', '=', rec.student_id.id),
                    ('is_primary', '=', True),
                    ('id', '!=', rec.id),
                ])
                if other:
                    raise ValidationError(
                        "Only one primary guardian is allowed per student.")
