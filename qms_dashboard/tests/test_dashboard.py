from odoo.tests.common import TransactionCase


class TestQmsDashboard(TransactionCase):
    def test_readiness_snapshot_is_bounded(self):
        dashboard = self.env["qms.dashboard"].create({"company_id": self.env.company.id})
        dashboard.action_refresh()
        self.assertGreaterEqual(dashboard.readiness_index, 0)
        self.assertLessEqual(dashboard.readiness_index, 100)

    def test_requirement_matrix_bridge_fields_exist(self):
        standard = self.env["qms.standard"].create({"name": "Internal Standard", "code": "INT-01", "company_id": self.env.company.id})
        clause = self.env["qms.standard.clause"].create({"standard_id": standard.id, "code": "1", "name": "General"})
        requirement = self.env["qms.requirement"].create({"name": "Document a process", "standard_id": standard.id, "clause_id": clause.id})
        self.assertEqual(requirement.support_score, 0)
        self.assertEqual(requirement.valid_evidence_count, 0)

    def test_dashboard_company_is_current_company(self):
        dashboard = self.env["qms.dashboard"].create({"company_id":self.env.company.id})
        self.assertEqual(dashboard.company_id, self.env.company)

    def test_dashboard_exposes_gap_count(self):
        dashboard = self.env["qms.dashboard"].create({"company_id":self.env.company.id})
        dashboard.action_refresh()
        self.assertGreaterEqual(dashboard.compliance_gap_count, 0)
