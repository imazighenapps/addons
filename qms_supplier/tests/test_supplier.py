from odoo.tests.common import TransactionCase


class TestQmsSupplier(TransactionCase):
    def test_supplier_evaluation_score(self):
        supplier = self.env["qms.supplier"].create({"partner_id": self.env.company.partner_id.id})
        evaluation = self.env["qms.supplier.evaluation"].create({
            "supplier_id": supplier.id,
            "quality_score": 80,
            "delivery_score": 90,
            "responsiveness_score": 70,
            "compliance_score": 100,
        })
        self.assertAlmostEqual(evaluation.overall_score, 85.0)
        self.assertAlmostEqual(supplier.latest_score, 85.0)

    def test_supplier_certificate_date_validation(self):
        supplier = self.env["qms.supplier"].create({"partner_id": self.env.company.partner_id.id})
        with self.assertRaises(Exception):
            self.env["qms.supplier.certificate"].create({
                "supplier_id": supplier.id,
                "name": "Invalid",
                "issue_date": "2026-10-10",
                "expiry_date": "2026-10-01",
            })

    def test_supplier_can_be_qualified(self):
        supplier = self.env["qms.supplier"].create({"partner_id": self.env.company.partner_id.id})
        supplier.action_qualify()
        self.assertEqual(supplier.qualification_status, "qualified")

    def test_supplier_scores_reject_out_of_range(self):
        supplier = self.env["qms.supplier"].create({"partner_id": self.env.company.partner_id.id})
        with self.assertRaises(Exception):
            self.env["qms.supplier.evaluation"].create({"supplier_id": supplier.id, "quality_score": 120, "delivery_score": 80, "responsiveness_score":80, "compliance_score":80})
