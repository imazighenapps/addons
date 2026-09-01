# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import EduflowTestCommon


@tagged('post_install', '-at_install')
class TestEduflowGradeLock(EduflowTestCommon):
    """F2.2 -- once an exam is validated, teachers can no longer edit
    grades, but Administration/Management/Admin still can."""

    def setUp(self):
        super().setUp()
        self.subject = self.env['eduflow.subject'].create({
            'code': 'MTH', 'name': 'Mathematics', 'level_id': self.level.id,
        })
        self.period = self.env['eduflow.academic.period'].create({
            'name': 'Term 1', 'year_id': self.year.id,
            'date_start': '2026-09-01', 'date_end': '2026-12-31',
        })
        self.exam = self.env['eduflow.exam'].create({
            'name': 'Test 1', 'classroom_id': self.classroom.id,
            'subject_id': self.subject.id, 'year_id': self.year.id,
            'period_id': self.period.id, 'date': '2026-10-01',
        })
        self.grade = self.env['eduflow.grade'].create({
            'exam_id': self.exam.id, 'student_id': self.student_1.id, 'grade': 12.0,
        })

    def test_teacher_can_edit_before_validation(self):
        self.grade.with_user(self.teacher_user).write({'grade': 15.0})
        self.assertEqual(self.grade.grade, 15.0)

    def test_teacher_cannot_edit_after_validation(self):
        self.exam.action_validate()
        with self.assertRaises(UserError):
            self.grade.with_user(self.teacher_user).write({'grade': 18.0})

    def test_admin_can_edit_after_validation(self):
        self.exam.action_validate()
        self.grade.write({'grade': 9.0})
        self.assertEqual(self.grade.grade, 9.0)

    def test_generate_grade_grid_prefills_students(self):
        self.env['eduflow.enrollment'].create({
            'student_id': self.student_2.id,
            'classroom_id': self.classroom.id,
            'year_id': self.year.id,
            'level_id': self.level.id,
            'date': '2026-09-01',
            'state': 'active',
        })
        self.exam.action_generate_grade_grid()
        self.assertIn(self.student_2, self.exam.grade_ids.mapped('student_id'))
