# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestToolboxTalk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "Toolbox Other Company"})
        cls.leader = cls.env["hr.employee"].create({
            "name": "Toolbox Test Leader"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "Toolbox Test Employee"})
        cls.employee_two = cls.env["hr.employee"].create({
            "name": "Toolbox Test Employee Two"})

    def _talk(self, **values):
        defaults = {
            "name": "Toolbox Test Briefing",
            "talk_on": date(2026, 11, 9),
            "location": "Workshop A",
            "leader_id": self.leader.id,
        }
        defaults.update(values)
        return self.env["toolbox.talk"].create(defaults)

    def _attendance(self, talk, employee=None, **values):
        defaults = {
            "talk_id": talk.id,
            "employee_id": (employee or self.employee).id,
        }
        defaults.update(values)
        return self.env["toolbox.attendance"].create(defaults)

    def test_01_talk_defaults(self):
        talk = self._talk()
        self.assertEqual(talk.state, "planned")
        self.assertEqual(talk.company_id, self.env.company)
        self.assertEqual(talk.attendance_count, 0)
        self.assertEqual(talk.signed_count, 0)

    def test_02_complete_talk(self):
        talk = self._talk()
        self.assertTrue(talk.action_complete())
        self.assertEqual(talk.state, "done")

    def test_03_double_complete_is_refused(self):
        talk = self._talk()
        talk.action_complete()
        with self.assertRaises(ValidationError):
            talk.action_complete()

    def test_04_attendance_defaults_and_sign(self):
        talk = self._talk()
        line = self._attendance(talk)
        self.assertFalse(line.signed)
        self.assertEqual(line.company_id, self.env.company)
        self.assertTrue(line.name.startswith("Attendance "))
        self.assertTrue(line.action_sign())
        self.assertTrue(line.signed)
        self.assertTrue(line.signed_on)

    def test_05_double_sign_is_refused(self):
        talk = self._talk()
        line = self._attendance(talk)
        line.action_sign()
        with self.assertRaises(ValidationError):
            line.action_sign()

    def test_06_attendance_counts(self):
        talk = self._talk()
        first = self._attendance(talk)
        self._attendance(talk, employee=self.employee_two, signed=False)
        first.action_sign()
        talk.invalidate_recordset()
        self.assertEqual(talk.attendance_count, 2)
        self.assertEqual(talk.signed_count, 1)

    def test_07_no_attendance_on_completed_talk(self):
        talk = self._talk()
        talk.action_complete()
        with self.assertRaises(ValidationError):
            self._attendance(talk)

    def test_08_duplicate_employee_is_refused(self):
        talk = self._talk()
        self._attendance(talk)
        with self.assertRaises(ValidationError):
            self._attendance(talk)

    def test_09_company_isolation(self):
        foreign_leader = self.env["hr.employee"].sudo().create({
            "name": "Toolbox Test Foreign Leader"})
        foreign = self.env["toolbox.talk"].with_company(
            self.other_company).sudo().create({
            "name": "Toolbox Foreign Talk",
            "talk_on": date(2026, 11, 9),
            "leader_id": foreign_leader.id,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._talk(name="Toolbox Local Talk")
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
