# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProbationReviewLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Probation Employee"})
        cls.reviewer = cls.env["hr.employee"].create({"name": "Probation Reviewer"})
        cls.manager = cls._user(
            "prl-manager",
            ["probation_review_log.group_probationrev_user"])
        cls.outsider = cls._user("prl-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _review(self, **vals):
        data = {
            "name": vals.pop("name", "PRL-TEST"),
            "employee_id": self.employee.id,
            "reviewer_id": self.reviewer.id,
            "date_start": self.today - timedelta(days=60),
            "date_end": self.today,
            "review_date": self.today,
            "score": 75,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["probation.review.log"].create(data)

    def test_01_create_review(self):
        rec = self._review()
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.outcome, "pending")
        self.assertTrue(rec.name)

    def test_02_submit_and_close(self):
        rec = self._review(outcome="passed")
        rec.action_submit()
        self.assertEqual(rec.state, "submitted")
        rec.action_close()
        self.assertEqual(rec.state, "closed")

    def test_03_close_requires_decision(self):
        rec = self._review()
        rec.action_submit()
        with self.assertRaises(UserError):
            rec.action_close()
        self.assertEqual(rec.state, "submitted")

    def test_04_invalid_transitions(self):
        rec = self._review(outcome="passed")
        with self.assertRaises(UserError):
            rec.action_close()
        rec.action_submit()
        with self.assertRaises(UserError):
            rec.action_submit()

    def test_05_constraints(self):
        with self.assertRaises(ValidationError):
            self._review(score=101)
        with self.assertRaises(ValidationError):
            self._review(score=-1)
        with self.assertRaises(ValidationError):
            self._review(date_end=self.today - timedelta(days=90))

    def test_06_cancel_and_reset(self):
        rec = self._review()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_07_access_control(self):
        with self.assertRaises(Exception):
            self.env["probation.review.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "employee_id": self.employee.id,
                    "date_start": self.today,
                    "date_end": self.today,
                    "review_date": self.today,
                    "company_id": self.env.company.id,
                })
        rec = self._review(name="PRL-ACC")
        rec.with_user(self.manager).read()

    def test_08_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "PRL B"})
        foreign = self.env["probation.review.log"].create({
            "name": "PRL-FOREIGN",
            "employee_id": self.employee.id,
            "date_start": self.today,
            "date_end": self.today,
            "review_date": self.today,
            "company_id": company_b.id,
        })
        visible = self.env["probation.review.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
