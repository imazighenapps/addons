from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestQmsTraining(TransactionCase):
    def setUp(self):
        super().setUp()
        self.course = self.env["qms.training.course"].create({"name": "Internal QMS Awareness", "company_id": self.env.company.id})
        self.assignment = self.env["qms.training.assignment"].create({"course_id": self.course.id, "employee_id": self.env.user.id, "minimum_score": 70, "score": 85})

    def test_completion_sets_expiry(self):
        self.assignment.action_mark_completed()
        self.assertEqual(self.assignment.state, "completed")
        self.assertEqual(self.assignment.completed_date, fields.Date.context_today(self.assignment))
        self.assertTrue(self.assignment.expiry_date)

    def test_low_score_rejected(self):
        self.assignment.score = 60
        with self.assertRaises(UserError):
            self.assignment.action_mark_completed()
