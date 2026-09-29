from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase


class QmsCoreTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.standard = cls.env["qms.standard"].create({
            "name": "Internal Management Framework",
            "code": "IMF",
            "version": "1.0",
        })
        cls.clause = cls.env["qms.standard.clause"].create({
            "standard_id": cls.standard.id,
            "code": "GOV-01",
            "name": "Governance",
        })
        cls.process = cls.env["qms.process"].create({
            "name": "Operations Control",
            "code": "PROC-01",
            "company_id": cls.company.id,
        })
        cls.requirement = cls.env["qms.requirement"].create({
            "name": "Controlled operational information",
            "standard_id": cls.standard.id,
            "clause_id": cls.clause.id,
            "process_ids": [(6, 0, [cls.process.id])],
        })

    def test_requirement_starts_without_support(self):
        self.assertEqual(self.requirement.compliance_state, "missing")

    def test_requirement_becomes_supported_with_valid_evidence(self):
        evidence = self.env["qms.evidence"].create({
            "name": "Approved operation record",
            "company_id": self.company.id,
            "requirement_ids": [(6, 0, [self.requirement.id])],
        })
        self.assertEqual(self.requirement.compliance_state, "missing")
        evidence.action_validate()
        self.assertEqual(self.requirement.compliance_state, "partial")
        self.requirement.action_mark_supported()
        self.assertEqual(self.requirement.compliance_state, "supported")
        self.assertTrue(evidence.integrity_hash)

    def test_cannot_mark_requirement_supported_without_evidence(self):
        with self.assertRaises(UserError):
            self.requirement.action_mark_supported()

    def test_clause_must_match_standard(self):
        other_standard = self.env["qms.standard"].create({
            "name": "Other Framework",
            "code": "OTHER",
            "version": "1.0",
        })
        with self.assertRaises(ValidationError):
            self.env["qms.requirement"].create({
                "name": "Invalid link",
                "standard_id": other_standard.id,
                "clause_id": self.clause.id,
            })

    def test_risk_score_and_level(self):
        risk = self.env["qms.risk"].create({
            "name": "Important process risk",
            "description": "Risk of process deviation during peak load.",
            "company_id": self.company.id,
            "likelihood": 5,
            "impact": 4,
            "residual_likelihood": 2,
            "residual_impact": 2,
        })
        self.assertEqual(risk.inherent_score, 20)
        self.assertEqual(risk.inherent_level, "critical")
        self.assertEqual(risk.residual_score, 4)
        self.assertEqual(risk.residual_level, "low")

    def test_standard_current_lifecycle(self):
        self.standard.action_set_current()
        self.assertEqual(self.standard.lifecycle_status, "current")
        self.standard.action_supersede()
        self.assertEqual(self.standard.lifecycle_status, "superseded")
        self.assertFalse(self.standard.active)

    def test_standard_metadata_model(self):
        standard = self.env["qms.standard"].create({"name": "Measurement Framework", "code": "MF-1", "version": "2026", "standard_family": "measurement", "is_certifiable": False})
        self.assertEqual(standard.standard_family, "measurement")
        self.assertFalse(standard.is_certifiable)

    def test_requirement_partial_assessment(self):
        self.requirement.action_assess_partial()
        self.assertEqual(self.requirement.implementation_status, "partial")
        self.assertEqual(self.requirement.compliance_state, "missing")

    def test_requirement_not_applicable_is_not_missing(self):
        self.requirement.action_mark_not_applicable()
        self.assertEqual(self.requirement.compliance_state, "supported")

    def test_clause_parent_must_share_standard(self):
        other_standard = self.env["qms.standard"].create({"name": "Other", "code": "OTHER-P", "version": "1"})
        other_clause = self.env["qms.standard.clause"].create({"standard_id": other_standard.id, "code": "O-1", "name": "Other"})
        with self.assertRaises(ValidationError):
            self.env["qms.standard.clause"].create({"standard_id": self.standard.id, "code": "GOV-02", "name": "Invalid", "parent_id": other_clause.id})

    def test_standard_transition_blocks_incomplete_mapping(self):
        from_standard = self.standard
        to_standard = self.env["qms.standard"].create({"name": "Internal Management Framework Next", "code": "IMF-N", "version": "2"})
        to_clause = self.env["qms.standard.clause"].create({"standard_id": to_standard.id, "code": "GOV-02", "name": "Governance"})
        to_req = self.env["qms.requirement"].create({"name": "Next control", "standard_id": to_standard.id, "clause_id": to_clause.id})
        transition = self.env["qms.standard.transition"].create({"name": "Framework transition", "source_standard_id": from_standard.id, "target_standard_id": to_standard.id})
        self.env["qms.standard.mapping"].create({"name": "Map Governance", "transition_id": transition.id, "company_id": self.env.company.id, "source_standard_id": from_standard.id, "target_standard_id": to_standard.id, "source_requirement_id": self.requirement.id, "target_requirement_id": to_req.id})
        with self.assertRaises(UserError):
            transition.action_complete()

    def test_standard_transition_completes_after_mapping_migrated(self):
        from_standard = self.standard
        to_standard = self.env["qms.standard"].create({"name": "Internal Management Framework Next 2", "code": "IMF-N2", "version": "2"})
        to_clause = self.env["qms.standard.clause"].create({"standard_id": to_standard.id, "code": "GOV-02", "name": "Governance"})
        to_req = self.env["qms.requirement"].create({"name": "Next control", "standard_id": to_standard.id, "clause_id": to_clause.id})
        transition = self.env["qms.standard.transition"].create({"name": "Framework transition 2", "source_standard_id": from_standard.id, "target_standard_id": to_standard.id})
        mapping = self.env["qms.standard.mapping"].create({"name": "Map Governance", "transition_id": transition.id, "company_id": self.env.company.id, "source_standard_id": from_standard.id, "target_standard_id": to_standard.id, "source_requirement_id": self.requirement.id, "target_requirement_id": to_req.id})
        mapping.status="migrated"
        transition.action_complete()
        self.assertEqual(transition.state, "completed")
