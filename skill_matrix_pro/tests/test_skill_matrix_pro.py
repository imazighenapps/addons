# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSkillMatrix(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "SkillMap Other Company"})
        cls.department = cls.env["hr.department"].create({
            "name": "SkillMap Production"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "SkillMap Test Employee",
            "department_id": cls.department.id,
        })
        cls.skill = cls.env["skill.skill"].create({
            "name": "SkillMap Forklift",
            "code": "FLT-1",
            "required_count": 2,
            "certification_required": True,
        })

    def _assignment(self, **values):
        defaults = {
            "skill_id": self.skill.id,
            "employee_id": self.employee.id,
            "level": "intermediate",
        }
        defaults.update(values)
        return self.env["skill.assignment"].create(defaults)

    def test_01_defaults(self):
        assignment = self._assignment()
        self.assertEqual(assignment.state, "draft")
        self.assertEqual(assignment.company_id, self.env.company)
        self.assertEqual(self.skill.holder_count, 1)
        self.assertEqual(self.skill.certified_count, 0)

    def test_02_certify_workflow(self):
        assignment = self._assignment()
        self.assertTrue(assignment.action_certify())
        self.assertEqual(assignment.state, "certified")
        self.assertTrue(assignment.certified_on)
        self.skill.invalidate_recordset()
        self.assertEqual(self.skill.certified_count, 1)

    def test_03_expire_workflow(self):
        assignment = self._assignment(certified_on="2026-02-01")
        assignment.action_certify()
        self.assertTrue(assignment.action_expire())
        self.assertEqual(assignment.state, "expired")

    def test_04_revoke_workflow(self):
        assignment = self._assignment(certified_on="2026-02-02")
        assignment.action_certify()
        self.assertTrue(assignment.action_revoke())
        self.assertEqual(assignment.state, "revoked")

    def test_05_double_certify_is_refused(self):
        assignment = self._assignment(certified_on="2026-02-03")
        assignment.action_certify()
        with self.assertRaises(ValidationError):
            assignment.action_certify()

    def test_06_revoke_draft_is_refused(self):
        assignment = self._assignment()
        with self.assertRaises(ValidationError):
            assignment.action_revoke()

    def test_07_duplicate_assignment_is_refused(self):
        self._assignment()
        with self.assertRaises(ValidationError):
            self._assignment()

    def test_08_date_constraints(self):
        with self.assertRaises(ValidationError):
            self._assignment(certified_on="2026-05-10",
                             expires_on="2026-05-01")

    def test_09_required_count_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["skill.skill"].create({
                "name": "SkillMap Bad",
                "required_count": -1,
            })

    def test_10_company_isolation(self):
        foreign_department = self.env["hr.department"].with_company(
            self.other_company).create({
            "name": "SkillMap Foreign Dept",
            "company_id": self.other_company.id,
        })
        foreign_employee = self.env["hr.employee"].with_company(
            self.other_company).create({
            "name": "SkillMap Foreign Employee",
            "company_id": self.other_company.id,
            "department_id": foreign_department.id,
        })
        foreign_skill = self.env["skill.skill"].with_company(
            self.other_company).create({
            "name": "SkillMap Foreign Skill",
            "company_id": self.other_company.id,
        })
        foreign_assignment = self.env["skill.assignment"].with_company(
            self.other_company).create({
            "skill_id": foreign_skill.id,
            "employee_id": foreign_employee.id,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign_skill.company_id, self.other_company)
        self.assertEqual(foreign_assignment.company_id, self.other_company)
        local = self._assignment()
        self.assertNotEqual(local.company_id, foreign_assignment.company_id)
