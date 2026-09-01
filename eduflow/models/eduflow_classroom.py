# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EduflowClassroom(models.Model):
    _name = "eduflow.classroom"
    _description = "Class"
    _order = "year_id desc, level_id, name"

    name = fields.Char(string="Class", required=True, help="E.g. 1st Year A")
    year_id = fields.Many2one("eduflow.academic.year", string="Academic Year", required=True)
    level_id = fields.Many2one("eduflow.level", string="Level", required=True)
    section = fields.Char(string="Section")
    principal_teacher_id = fields.Many2one("eduflow.teacher", string="Homeroom Teacher")
    capacity = fields.Integer(string="Maximum Capacity", default=30)
    enrollment_ids = fields.One2many("eduflow.enrollment", "classroom_id", string="Enrollments")
    timetable_ids = fields.One2many("eduflow.timetable.session", "classroom_id", string="Timetable")
    student_count = fields.Integer(string="Enrollment Count", compute="_compute_student_count", store=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    _sql_constraints = [
        ("name_year_uniq", "unique(name, year_id)",
         "This class already exists for this academic year."),
    ]

    @api.depends("enrollment_ids.state")
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.enrollment_ids.filtered(
                lambda e: e.state in ("confirmed", "active")))

    @api.constrains("capacity")
    def _check_capacity(self):
        for rec in self:
            if rec.capacity <= 0:
                raise ValidationError("Maximum capacity must be greater than zero.")
