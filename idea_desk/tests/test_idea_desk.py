# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIdeaDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "IdeaDesk Other Company"})
        cls.author = cls.env["res.partner"].create({
            "name": "IdeaDesk Test Author"})
        cls.reviewer = cls.env["res.partner"].create({
            "name": "IdeaDesk Test Reviewer"})

    def _idea(self, **values):
        defaults = {
            "name": "IdeaDesk Test Idea",
            "author_id": self.author.id,
            "area": "Warehouse",
            "expected_gain": 120.0,
            "submitted_on": date(2026, 11, 9),
        }
        defaults.update(values)
        return self.env["idea.proposal"].create(defaults)

    def test_01_idea_defaults(self):
        idea = self._idea()
        self.assertEqual(idea.state, "submitted")
        self.assertEqual(idea.company_id, self.env.company)
        self.assertEqual(idea.review_count, 0)
        self.assertFalse(idea.evaluated_on)

    def test_02_accept_sets_evaluated_date(self):
        idea = self._idea()
        self.assertTrue(idea.action_accept())
        self.assertEqual(idea.state, "accepted")
        self.assertTrue(idea.evaluated_on)

    def test_03_reject_sets_evaluated_date(self):
        idea = self._idea(name="IdeaDesk Test Rejected Idea")
        self.assertTrue(idea.action_reject())
        self.assertEqual(idea.state, "rejected")
        self.assertTrue(idea.evaluated_on)

    def test_04_implement_requires_accepted_state(self):
        idea = self._idea(name="IdeaDesk Test Impl Idea")
        with self.assertRaises(ValidationError):
            idea.action_implement()
        idea.action_accept()
        self.assertTrue(idea.action_implement())
        self.assertEqual(idea.state, "implemented")
        self.assertTrue(idea.implemented_on)

    def test_05_double_evaluation_is_refused(self):
        idea = self._idea(name="IdeaDesk Test Double Idea")
        idea.action_accept()
        with self.assertRaises(ValidationError):
            idea.action_reject()
        with self.assertRaises(ValidationError):
            idea.action_accept()

    def test_06_negative_expected_gain_is_refused(self):
        with self.assertRaises(ValidationError):
            self._idea(name="IdeaDesk Negative Gain", expected_gain=-5.0)

    def test_07_review_count(self):
        idea = self._idea(name="IdeaDesk Counted Idea")
        self.env["idea.review"].create({
            "proposal_id": idea.id,
            "reviewer_id": self.reviewer.id,
            "decision": "accept",
            "reviewed_on": date(2026, 11, 10),
        })
        idea.invalidate_recordset()
        self.assertEqual(idea.review_count, 1)

    def test_08_review_defaults(self):
        idea = self._idea(name="IdeaDesk Review Defaults")
        review = self.env["idea.review"].create({
            "proposal_id": idea.id,
            "reviewer_id": self.reviewer.id,
            "reviewed_on": date(2026, 11, 10),
        })
        self.assertEqual(review.decision, "note")
        self.assertEqual(review.company_id, self.env.company)
        self.assertTrue(review.name.startswith("Review "))

    def test_09_company_isolation(self):
        foreign_author = self.env["res.partner"].sudo().create({
            "name": "IdeaDesk Test Foreign Author"})
        foreign = self.env["idea.proposal"].with_company(
            self.other_company).sudo().create({
            "name": "IdeaDesk Foreign Idea",
            "author_id": foreign_author.id,
            "submitted_on": date(2026, 11, 9),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._idea(name="IdeaDesk Local Idea")
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
