from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestQmsImprovement(TransactionCase):
    def test_completion_and_standardization(self):
        record = self.env['qms.improvement'].create({'name': 'Reduce setup time', 'description': 'Test'})
        record.action_approve(); record.action_start()
        with self.assertRaises(UserError):
            record.action_complete()
        record.lessons_learned = 'Standard work updated.'
        record.action_complete(); record.action_standardize()
        self.assertEqual(record.status, 'standardized')

    def test_rejected_improvement_can_be_rejected(self):
        record = self.env["qms.improvement"].create({"name":"Rejected idea","description":"Test"})
        record.action_cancel()
        self.assertEqual(record.status, "cancelled")

    def test_standardized_improvement_retains_lessons(self):
        record = self.env["qms.improvement"].create({"name":"Standardize","description":"Test"})
        record.action_approve(); record.action_start(); record.lessons_learned="Standard updated"; record.action_complete(); record.action_standardize()
        self.assertEqual(record.lessons_learned, "Standard updated")
