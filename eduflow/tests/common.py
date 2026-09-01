# -*- coding: utf-8 -*-
from odoo.tests import common


class EduflowTestCommon(common.TransactionCase):
    """Shared fixtures: an active academic year, a level, a
    small capacity class (to test constraint), a teacher
    and two distinct student/parent pairs (to test isolation of
    ir.rule between families)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.year = cls.env['eduflow.academic.year'].create({
            'name': '2026/2027',
            'date_start': '2026-09-01',
            'date_end': '2027-06-30',
            'active_year': True,
        })
        cls.level = cls.env['eduflow.level'].create({'name': 'Test Level'})
        cls.classroom = cls.env['eduflow.classroom'].create({
            'name': 'Test Classroom A',
            'year_id': cls.year.id,
            'level_id': cls.level.id,
            'capacity': 1,
        })

        cls.teacher_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test Teacher',
            'login': 'eduflow_test_teacher@example.com',
            'email': 'eduflow_test_teacher@example.com',
            'groups_id': [(6, 0, [cls.env.ref('eduflow.group_eduflow_teacher').id])],
        })
        cls.teacher = cls.env['eduflow.teacher'].create({
            'name': 'Test Teacher',
            'user_id': cls.teacher_user.id,
        })
        cls.classroom.principal_teacher_id = cls.teacher.id

        # Famille 1
        cls.parent_1_partner = cls.env['res.partner'].create({'name': 'Parent Un'})
        cls.parent_1_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Parent Un',
            'login': 'eduflow_test_parent1@example.com',
            'email': 'eduflow_test_parent1@example.com',
            'partner_id': cls.parent_1_partner.id,
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id,
                                   cls.env.ref('eduflow.group_eduflow_parent_portal').id])],
        })
        cls.parent_1 = cls.env['eduflow.parent'].create({
            'name': 'Parent Un',
            'partner_id': cls.parent_1_partner.id,
            'portal_access': True,
        })
        cls.student_1 = cls.env['eduflow.student'].create({
            'name': 'Eleve', 'firstname': 'Un', 'status': 'active',
        })
        cls.env['eduflow.student.parent.rel'].create({
            'student_id': cls.student_1.id,
            'parent_id': cls.parent_1.id,
            'relation': 'father',
            'is_primary': True,
        })

        # Family 2 (to verify isolation)
        cls.parent_2_partner = cls.env['res.partner'].create({'name': 'Parent Deux'})
        cls.parent_2_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Parent Deux',
            'login': 'eduflow_test_parent2@example.com',
            'email': 'eduflow_test_parent2@example.com',
            'partner_id': cls.parent_2_partner.id,
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id,
                                   cls.env.ref('eduflow.group_eduflow_parent_portal').id])],
        })
        cls.parent_2 = cls.env['eduflow.parent'].create({
            'name': 'Parent Deux',
            'partner_id': cls.parent_2_partner.id,
            'portal_access': True,
        })
        cls.student_2 = cls.env['eduflow.student'].create({
            'name': 'Eleve', 'firstname': 'Deux', 'status': 'active',
        })
        cls.env['eduflow.student.parent.rel'].create({
            'student_id': cls.student_2.id,
            'parent_id': cls.parent_2.id,
            'relation': 'mother',
            'is_primary': True,
        })
