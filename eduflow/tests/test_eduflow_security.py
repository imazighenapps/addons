# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import EduflowTestCommon


@tagged('post_install', '-at_install')
class TestEduflowSecurity(EduflowTestCommon):

    def test_parent_sees_only_own_child(self):
        """A parent must only see their own child, never
        another family's (ir.rule rule_parent_portal_own_children)."""
        Student = self.env['eduflow.student'].with_user(self.parent_1_user)
        own_child = Student.browse(self.student_1.id)
        self.assertEqual(own_child.name, self.student_1.name)

        other_child = Student.browse(self.student_2.id)
        with self.assertRaises(AccessError):
            other_child.name  # noqa: B018 - force read, thus rule verification

    def test_parent_group_auto_synced_on_user_creation(self):
        """Regression: creating a portal user linked to the contact of a
        eduflow.parent record must automatically give them the
        business group, otherwise the portal remains empty (see ResUsers._eduflow_
        sync_parent_portal_group)."""
        partner = self.env['res.partner'].create({'name': 'Parent Trois'})
        parent = self.env['eduflow.parent'].create({
            'name': 'Parent Trois', 'partner_id': partner.id,
        })
        group = self.env.ref('eduflow.group_eduflow_parent_portal')
        user = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Parent Trois',
            'login': 'eduflow_test_parent3@example.com',
            'email': 'eduflow_test_parent3@example.com',
            'partner_id': partner.id,
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
        })
        self.assertIn(group.id, user.groups_id.ids)
        self.assertTrue(parent.portal_access)

    def test_teacher_cannot_access_other_teacher_exam(self):
        """A teacher must not be able to view a colleague's exams (rule_teacher_exam_own)."""
        other_teacher_user = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Other Teacher',
            'login': 'eduflow_test_other_teacher@example.com',
            'email': 'eduflow_test_other_teacher@example.com',
            'groups_id': [(6, 0, [self.env.ref('eduflow.group_eduflow_teacher').id])],
        })
        subject = self.env['eduflow.subject'].create({
            'code': 'HIST', 'name': 'History', 'level_id': self.level.id,
        })
        period = self.env['eduflow.academic.period'].create({
            'name': 'Trimester 1', 'year_id': self.year.id,
            'date_start': '2026-09-01', 'date_end': '2026-12-01',
        })
        exam = self.env['eduflow.exam'].create({
            'name': 'History Test', 'year_id': self.year.id, 'period_id': period.id,
            'classroom_id': self.classroom.id, 'subject_id': subject.id,
            'teacher_id': self.teacher.id,
        })
        exam_as_other = self.env['eduflow.exam'].with_user(other_teacher_user).browse(exam.id)
        with self.assertRaises(AccessError):
            exam_as_other.name

    def test_teacher_cannot_access_other_teacher_report_card(self):
        """Audit 2026-08-31: a teacher must not read report cards of another teacher's classes (rule_teacher_report_card_own_classes)."""
        other_teacher_user = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Other Teacher RC',
            'login': 'eduflow_test_other_teacher_rc@example.com',
            'email': 'eduflow_test_other_teacher_rc@example.com',
            'groups_id': [(6, 0, [self.env.ref('eduflow.group_eduflow_teacher').id])],
        })
        period = self.env['eduflow.academic.period'].create({
            'name': 'Trimester 1 RC', 'year_id': self.year.id,
            'date_start': '2026-09-01', 'date_end': '2026-12-01',
        })
        # Create a report card for student_1 in teacher's class
        report = self.env['eduflow.report.card'].create({
            'student_id': self.student_1.id,
            'classroom_id': self.classroom.id,
            'year_id': self.year.id,
            'period_id': period.id,
        })
        report_as_other = self.env['eduflow.report.card'].with_user(other_teacher_user).browse(report.id)
        with self.assertRaises(AccessError):
            report_as_other.name
        # Same for line
        line = self.env['eduflow.report.card.line'].create({
            'report_card_id': report.id,
            'subject_id': self.env['eduflow.subject'].create({'code': 'MUS', 'name': 'Music', 'level_id': self.level.id}).id,
            'average': 12.0,
        })
        line_as_other = self.env['eduflow.report.card.line'].with_user(other_teacher_user).browse(line.id)
        with self.assertRaises(AccessError):
            line_as_other.average

    def test_admin_group_not_restricted_by_teacher_rules(self):
        """Regression: group_eduflow_admin implies group_eduflow_teacher,
        hence teacher scope rules must not restrict
        an administrator (bypass has_group in domain_force)."""
        admin_user = self.env.ref('base.user_admin')
        subject = self.env['eduflow.subject'].create({
            'code': 'SVT', 'name': 'Biology', 'level_id': self.level.id,
        })
        period = self.env['eduflow.academic.period'].create({
            'name': 'Trimester 1', 'year_id': self.year.id,
            'date_start': '2026-09-01', 'date_end': '2026-12-01',
        })
        exam = self.env['eduflow.exam'].create({
            'name': 'Biology Test', 'year_id': self.year.id, 'period_id': period.id,
            'classroom_id': self.classroom.id, 'subject_id': subject.id,
            'teacher_id': self.teacher.id,  # belongs to ANOTHER teacher
        })
        exam_as_admin = self.env['eduflow.exam'].with_user(admin_user).browse(exam.id)
        self.assertEqual(exam_as_admin.name, 'Biology Test')
