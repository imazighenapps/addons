from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestQmsAudit(TransactionCase):
    def test_audit_cannot_start_without_checks(self):
        audit = self.env["qms.audit"].create({"name": "Internal Audit", "scope": "Operations"})
        audit.action_schedule()
        with self.assertRaises(UserError):
            audit.action_start()

    def test_audit_cannot_close_with_unchecked_line(self):
        audit = self.env["qms.audit"].create({"name": "Internal Audit", "scope": "Operations", "risk_basis": "High-risk processes in scope"})
        self.env["qms.audit.line"].create({"audit_id": audit.id, "question": "Are records controlled?"})
        audit.action_schedule(); audit.action_start()
        with self.assertRaises(UserError):
            audit.action_generate_report()

    def test_risk_based_audit_requires_risk_basis(self):
        audit = self.env["qms.audit"].create({"name": "Risk Audit", "scope": "Operations", "risk_based": True})
        self.env["qms.audit.line"].create({"audit_id": audit.id, "question": "Control is effective"})
        audit.action_schedule()
        with self.assertRaises(UserError):
            audit.action_start()

    def test_risk_based_audit_starts_with_risk_basis(self):
        audit = self.env["qms.audit"].create({"name": "Risk Audit 2", "scope": "Operations", "risk_based": True, "risk_basis": "High residual risk"})
        self.env["qms.audit.line"].create({"audit_id": audit.id, "question": "Control is effective"})
        audit.action_schedule(); audit.action_start()
        self.assertEqual(audit.state, "in_progress")

    def test_audit_program_completion_rate(self):
        program = self.env["qms.audit.program"].create({"name": "Annual Program", "year": 2026})
        audit = self.env["qms.audit"].create({"name": "Program Audit", "scope": "Operations", "program_id": program.id, "risk_based": False})
        self.assertEqual(program.audit_count, 1)
        self.assertEqual(program.completion_rate, 0)
        audit.action_schedule()
        line = self.env["qms.audit.line"].create({"audit_id": audit.id, "question": "Check"})
        audit.action_start()
        line.result = "conform"
        audit.action_generate_report(); audit.action_close()
        self.assertEqual(program.completion_rate, 100)
