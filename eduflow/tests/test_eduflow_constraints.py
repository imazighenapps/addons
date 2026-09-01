# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import EduflowTestCommon


@tagged('post_install', '-at_install')
class TestEduflowConstraints(EduflowTestCommon):

    def test_classroom_capacity_enforced(self):
        """Test class has capacity 1: a second confirmed
        enrollment must be refused."""
        Enrollment = self.env['eduflow.enrollment']
        Enrollment.create({
            'student_id': self.student_1.id,
            'year_id': self.year.id,
            'level_id': self.level.id,
            'classroom_id': self.classroom.id,
            'state': 'confirmed',
        })
        with self.assertRaises(ValidationError):
            Enrollment.create({
                'student_id': self.student_2.id,
                'year_id': self.year.id,
                'level_id': self.level.id,
                'classroom_id': self.classroom.id,
                'state': 'confirmed',
            })

    def test_single_primary_parent_per_student(self):
        """Only one primary guardian is allowed per student."""
        with self.assertRaises(ValidationError):
            self.env['eduflow.student.parent.rel'].create({
                'student_id': self.student_1.id,
                'parent_id': self.parent_2.id,
                'relation': 'guardian',
                'is_primary': True,
            })

    def test_single_active_year_per_company(self):
        """Only one active academic year per institution."""
        with self.assertRaises(ValidationError):
            self.env['eduflow.academic.year'].create({
                'name': '2027/2028',
                'date_start': '2027-09-01',
                'date_end': '2028-06-30',
                'active_year': True,
            })

    def test_timetable_teacher_conflict_detected(self):
        """Same teacher cannot be on two sessions that
        overlap, even in two different classes."""
        other_classroom = self.env['eduflow.classroom'].create({
            'name': 'Test Classroom B',
            'year_id': self.year.id,
            'level_id': self.level.id,
            'capacity': 30,
        })
        subject = self.env['eduflow.subject'].create({
            'code': 'MATH', 'name': 'Mathematics', 'level_id': self.level.id,
        })
        self.env['eduflow.timetable.session'].create({
            'classroom_id': self.classroom.id,
            'subject_id': subject.id,
            'teacher_id': self.teacher.id,
            'day': '0',
            'hour_start': 8.0,
            'hour_end': 9.0,
        })
        with self.assertRaises(ValidationError):
            self.env['eduflow.timetable.session'].create({
                'classroom_id': other_classroom.id,
                'subject_id': subject.id,
                'teacher_id': self.teacher.id,
                'day': '0',
                'hour_start': 8.5,
                'hour_end': 9.5,
            })

    def test_report_card_ranking_updates_when_classmate_average_changes(self):
        """Non-regression: ranking (not stored) must reflect the
        current averages of the whole class, even if another report card has
        been modified after generation (cf. bug of stored
        fields with incomplete dependencies)."""
        period = self.env['eduflow.academic.period'].create({
            'name': 'Trimester 1', 'year_id': self.year.id,
            'date_start': '2026-09-01', 'date_end': '2026-12-01',
        })
        rc_1 = self.env['eduflow.report.card'].create({
            'student_id': self.student_1.id, 'classroom_id': self.classroom.id,
            'year_id': self.year.id, 'period_id': period.id,
        })
        rc_2 = self.env['eduflow.report.card'].create({
            'student_id': self.student_2.id, 'classroom_id': self.classroom.id,
            'year_id': self.year.id, 'period_id': period.id,
        })
        subject = self.env['eduflow.subject'].create({
            'code': 'FR', 'name': 'French', 'level_id': self.level.id,
        })
        self.env['eduflow.report.card.line'].create({
            'report_card_id': rc_1.id, 'subject_id': subject.id, 'average': 10.0,
        })
        self.env['eduflow.report.card.line'].create({
            'report_card_id': rc_2.id, 'subject_id': subject.id, 'average': 15.0,
        })
        self.assertEqual(rc_2.ranking, 1, "rc_2 (15/20) must rank before rc_1 (10/20)")

        # We improve rc_1 average afterwards: its ranking
        # AND that of rc_2 must update, without regenerating rc_2.
        rc_1.line_ids.unlink()
        self.env['eduflow.report.card.line'].create({
            'report_card_id': rc_1.id, 'subject_id': subject.id, 'average': 18.0,
        })
        self.assertEqual(rc_1.ranking, 1, "rc_1 (18/20) must now overtake rc_2 (15/20)")
        self.assertEqual(rc_2.ranking, 2)
