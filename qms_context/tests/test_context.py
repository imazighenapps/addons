from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestQmsContext(TransactionCase):
    def test_opportunity_completion_requires_result(self):
        opp = self.env["qms.opportunity"].create({"name": "Improve first-pass yield", "description": "Test", "status": "in_progress"})
        with self.assertRaises(UserError):
            opp.action_complete()
        opp.result = "Measured improvement achieved."
        opp.action_complete()
        self.assertEqual(opp.status, "completed")

    def test_scope_approval(self):
        scope = self.env["qms.management.scope"].create({"name": "Corporate QMS", "scope_text": "Corporate operations"})
        scope.action_approve()
        self.assertEqual(scope.state, "approved")

    def test_interest_party_can_be_marked_relevant(self):
        party = self.env["qms.interested.party"].create({"name":"Customers","needs_expectations":"Reliable delivery","category":"customer"})
        self.assertTrue(party.relevant)

    def test_compliance_obligation_rejects_invalid_date_order(self):
        from odoo.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.env["qms.compliance.obligation"].create({"name":"License","description":"Test","review_date":"2026-12-01","next_review_date":"2026-11-01"})
