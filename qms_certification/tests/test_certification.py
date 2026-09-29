from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestQmsCertification(TransactionCase):
    def test_activation_requires_dates(self):
        standard = self.env["qms.standard"].create({"name": "Internal Framework", "code": "IF-1", "version": "1"})
        certification = self.env["qms.certification"].create({
            "name": "Quality Certificate",
            "standard_id": standard.id,
            "certificate_number": "CERT-001",
            "scope": "Quality management",
        })
        with self.assertRaises(ValidationError):
            certification.action_activate()

    def test_certificate_can_activate_with_valid_dates(self):
        standard = self.env["qms.standard"].create({"name": "Internal Framework", "code": "IF-2", "version": "1"})
        certification = self.env["qms.certification"].create({
            "name": "Quality Certificate",
            "standard_id": standard.id,
            "certificate_number": "CERT-002",
            "scope": "Quality management",
            "issue_date": "2026-01-01",
            "expiry_date": "2027-01-01",
        })
        certification.action_activate()
        self.assertEqual(certification.status, "active")

    def test_certificate_can_be_suspended(self):
        standard = self.env["qms.standard"].create({"name":"Certification Standard","code":"CERT-S","version":"1"})
        certification = self.env["qms.certification"].create({"name":"Cert","standard_id":standard.id,"certificate_number":"CERT-S-01","scope":"QMS","issue_date":"2026-01-01","expiry_date":"2027-01-01"})
        certification.action_activate(); certification.action_suspend()
        self.assertEqual(certification.status, "suspended")

    def test_certificate_can_be_renewed(self):
        standard = self.env["qms.standard"].create({"name":"Certification Standard 2","code":"CERT-S2","version":"1"})
        certification = self.env["qms.certification"].create({"name":"Cert 2","standard_id":standard.id,"certificate_number":"CERT-S2-01","scope":"QMS","issue_date":"2026-01-01","expiry_date":"2027-01-01"})
        certification.action_mark_renewed()
        self.assertEqual(certification.status, "renewed")
