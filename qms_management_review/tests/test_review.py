from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestQmsManagementReview(TransactionCase):
    def test_prepare_snapshot_and_close_guard(self):
        review = self.env["qms.management.review"].create({"name": "Quarterly QMS Review", "company_id": self.env.company.id})
        review.action_prepare_snapshot()
        self.assertEqual(review.state, "prepared")
        review.action_mark_held()
        self.assertEqual(review.state, "held")
        action = self.env["qms.management.action"].create({"review_id": review.id, "name": "Update process KPI"})
        with self.assertRaises(UserError):
            review.action_close()
        action.action_done()
        review.action_close()
        self.assertEqual(review.state, "closed")

    def test_review_requires_actions_done_before_close(self):
        review = self.env["qms.management.review"].create({"name":"Review 2","company_id":self.env.company.id})
        review.action_prepare_snapshot(); review.action_mark_held()
        action = self.env["qms.management.action"].create({"review_id":review.id,"name":"Close action"})
        with self.assertRaises(UserError):
            review.action_close()
        self.assertEqual(action.status, "planned")
