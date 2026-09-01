# -*- coding: utf-8 -*-
from odoo.tests import tagged

from .common import EduflowTestCommon


@tagged('post_install', '-at_install')
class TestEduflowMultiCompany(EduflowTestCommon):
    """F4.1 -- a user restricted to company A must not see records
    (students, fees...) that belong to company B."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_b = cls.env['res.company'].create({'name': 'EduFlow School B'})
        cls.admin_user = cls.env.ref('base.user_admin')
        cls.admin_user.write({
            'company_ids': [(4, cls.company_b.id)],
        })
        cls.student_b = cls.env['eduflow.student'].with_company(cls.company_b).create({
            'name': 'Eleve', 'firstname': 'CompanyB', 'status': 'active',
            'company_id': cls.company_b.id,
        })

    def test_company_a_user_does_not_see_company_b_student(self):
        students = self.env['eduflow.student'].with_user(self.admin_user).with_context(
            allowed_company_ids=[self.env.company.id]).search([])
        self.assertNotIn(self.student_b, students)

    def test_company_b_user_sees_its_own_student(self):
        students = self.env['eduflow.student'].with_user(self.admin_user).with_context(
            allowed_company_ids=[self.company_b.id]).search([])
        self.assertIn(self.student_b, students)
