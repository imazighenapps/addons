# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTrainingDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "TrainBook Other Company"})
        cls.department = cls.env["hr.department"].create({
            "name": "TrainBook Academy"})
        cls.trainer = cls.env["hr.employee"].create({
            "name": "TrainBook Test Trainer",
            "department_id": cls.department.id,
        })
        cls.participant = cls.env["hr.employee"].create({
            "name": "TrainBook Test Participant",
            "department_id": cls.department.id,
        })

    def _session(self, **values):
        defaults = {
            "name": "TrainBook Session 2026-A",
            "topic": "Safety Basics",
            "trainer_id": self.trainer.id,
            "date_start": "2026-06-10",
            "date_end": "2026-06-10",
            "capacity": 10,
        }
        defaults.update(values)
        return self.env["training.session"].create(defaults)

    def _attendance(self, session, employee=None, **values):
        defaults = {
            "session_id": session.id,
            "employee_id": (employee or self.participant).id,
        }
        defaults.update(values)
        return self.env["training.attendance"].create(defaults)

    def test_01_session_defaults(self):
        session = self._session()
        self.assertEqual(session.state, "draft")
        self.assertEqual(session.company_id, self.env.company)
        self.assertEqual(session.attendee_count, 0)
        self.assertEqual(session.certificate_count, 0)

    def test_02_workflow_confirm_done(self):
        session = self._session(name="TrainBook Session 2026-B")
        self.assertTrue(session.action_confirm())
        self.assertEqual(session.state, "confirmed")
        self.assertTrue(session.action_done())
        self.assertEqual(session.state, "done")

    def test_03_cancel_and_reset(self):
        session = self._session(name="TrainBook Session 2026-C")
        session.action_confirm()
        self.assertTrue(session.action_cancel())
        self.assertEqual(session.state, "cancelled")
        self.assertTrue(session.action_reset_draft())
        self.assertEqual(session.state, "draft")

    def test_04_done_cannot_be_cancelled(self):
        session = self._session(name="TrainBook Session 2026-D")
        session.action_confirm()
        session.action_done()
        with self.assertRaises(ValidationError):
            session.action_cancel()

    def test_05_attendance_counters(self):
        session = self._session(name="TrainBook Session 2026-E")
        att = self._attendance(session)
        self.assertEqual(session.attendee_count, 0)
        att.action_mark_present()
        att.action_issue_certificate()
        session.invalidate_recordset()
        self.assertEqual(session.attendee_count, 1)
        self.assertEqual(session.certificate_count, 1)

    def test_06_duplicate_participant_is_refused(self):
        session = self._session(name="TrainBook Session 2026-F")
        self._attendance(session)
        with self.assertRaises(ValidationError):
            self._attendance(session)

    def test_07_certificate_requires_presence(self):
        session = self._session(name="TrainBook Session 2026-G")
        att = self._attendance(session)
        with self.assertRaises(ValidationError):
            att.action_issue_certificate()

    def test_08_date_and_capacity_constraints(self):
        with self.assertRaises(ValidationError):
            self._session(name="TrainBook Session 2026-H",
                          date_start="2026-06-12", date_end="2026-06-11")
        with self.assertRaises(ValidationError):
            self._session(name="TrainBook Session 2026-I", capacity=0)

    def test_09_capacity_limit(self):
        session = self._session(name="TrainBook Session 2026-J", capacity=1)
        self._attendance(session)
        other = self.env["hr.employee"].create({
            "name": "TrainBook Extra Participant"})
        with self.assertRaises(ValidationError):
            self._attendance(session, employee=other)

    def test_10_company_isolation(self):
        foreign_department = self.env["hr.department"].with_company(
            self.other_company).create({
            "name": "TrainBook Foreign Dept",
            "company_id": self.other_company.id,
        })
        foreign_trainer = self.env["hr.employee"].with_company(
            self.other_company).create({
            "name": "TrainBook Foreign Trainer",
            "company_id": self.other_company.id,
            "department_id": foreign_department.id,
        })
        foreign_session = self.env["training.session"].with_company(
            self.other_company).create({
            "name": "TrainBook Foreign Session",
            "topic": "Foreign Topic",
            "trainer_id": foreign_trainer.id,
            "date_start": "2026-07-01",
            "date_end": "2026-07-01",
            "capacity": 5,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign_session.company_id, self.other_company)
        local = self._session(name="TrainBook Local Session 2026-K")
        self.assertNotEqual(local.company_id, foreign_session.company_id)
