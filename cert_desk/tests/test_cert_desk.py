# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSupplierCert(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "CertDesk Other Company"})
        cls.supplier = cls.env["res.partner"].create({
            "name": "CertDesk Test Supplier 2026"})

    def _cert(self, **values):
        defaults = {
            "name": "CertDesk ISO 2026",
            "partner_id": self.supplier.id,
            "cert_type": "iso",
            "reference": "ISO-2026-001",
            "issue_date": date(2026, 1, 10),
            "expiry_date": date(2027, 1, 10),
        }
        defaults.update(values)
        return self.env["cert.document"].create(defaults)

    def test_01_defaults_and_reminder(self):
        cert = self._cert()
        self.assertEqual(cert.state, "draft")
        self.assertEqual(cert.company_id, self.env.company)
        self.assertTrue(cert.reminder_date)
        self.assertFalse(cert.blocked)

    def test_02_valid_expiring_expired_flow(self):
        cert = self._cert(name="CertDesk Flow 2026")
        self.assertTrue(cert.action_mark_valid())
        self.assertEqual(cert.state, "valid")
        self.assertTrue(cert.action_mark_expiring())
        self.assertEqual(cert.state, "expiring")
        self.assertTrue(cert.action_mark_expired())
        self.assertEqual(cert.state, "expired")
        self.assertTrue(cert.blocked)

    def test_03_renew_creates_history(self):
        cert = self._cert(name="CertDesk Renew 2026")
        cert.action_mark_valid()
        cert.action_mark_expired()
        self.assertTrue(cert.action_renew())
        cert.invalidate_recordset()
        self.assertEqual(cert.state, "renewed")
        self.assertEqual(cert.renewal_count, 1)
        self.assertEqual(len(cert.renewal_ids), 1)
        renewal = cert.renewal_ids[0]
        self.assertEqual(renewal.new_expiry_date, cert.expiry_date)

    def test_04_date_constraint(self):
        with self.assertRaises(ValidationError):
            self._cert(name="CertDesk Bad Date 2026",
                       issue_date=date(2026, 5, 1),
                       expiry_date=date(2026, 4, 1))

    def test_05_renewal_date_constraint(self):
        cert = self._cert(name="CertDesk Renewal Constraint 2026")
        with self.assertRaises(ValidationError):
            self.env["cert.renewal"].create({
                "certificate_id": cert.id,
                "new_issue_date": date(2026, 6, 1),
                "new_expiry_date": date(2026, 5, 1),
            })

    def test_06_invalid_transitions(self):
        cert = self._cert(name="CertDesk Invalid 2026")
        with self.assertRaises(UserError):
            cert.action_mark_expiring()
        cert.action_mark_valid()
        with self.assertRaises(UserError):
            cert.action_renew()

    def test_07_expired_certificate_cannot_be_validated(self):
        cert = self._cert(name="CertDesk Expired 2026",
                          issue_date=date(2026, 1, 1),
                          expiry_date=date(2026, 2, 1))
        with self.assertRaises(UserError):
            cert.action_mark_valid()

    def test_08_renewal_count_updates(self):
        cert = self._cert(name="CertDesk Count 2026")
        self.env["cert.renewal"].create({
            "certificate_id": cert.id,
            "new_issue_date": date(2027, 1, 10),
            "new_expiry_date": date(2028, 1, 10),
        })
        cert.invalidate_recordset()
        self.assertEqual(cert.renewal_count, 1)

    def test_09_company_isolation(self):
        foreign_supplier = self.env["res.partner"].with_company(
            self.other_company).sudo().create({
            "name": "CertDesk Foreign Supplier 2026"})
        foreign = self.env["cert.document"].with_company(
            self.other_company).sudo().create({
            "name": "Foreign Cert 2026",
            "partner_id": foreign_supplier.id,
            "cert_type": "halal",
            "issue_date": date(2026, 3, 1),
            "expiry_date": date(2027, 3, 1),
            "company_id": self.other_company.id,
        })
        local = self._cert(name="CertDesk Local 2026")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
