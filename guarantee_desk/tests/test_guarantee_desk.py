# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGuaranteeDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "GuaranteeDesk Other Company"})
        cls.beneficiary = cls.env["res.partner"].create({
            "name": "GuaranteeDesk Beneficiary"})
        cls.bank = cls.env["res.partner"].create({
            "name": "GuaranteeDesk Issuing Bank"})
        cls.guarantee = cls.env["bank.guarantee"].create({
            "name": "BG-2026-001",
            "guarantee_type": "performance",
            "beneficiary_id": cls.beneficiary.id,
            "issuing_bank_id": cls.bank.id,
            "amount": 25000.0,
            "issue_date": date(2026, 1, 10),
            "expiry_date": date(2027, 1, 10),
        })

    def test_01_guarantee_defaults(self):
        self.assertEqual(self.guarantee.state, "draft")
        self.assertEqual(self.guarantee.company_id, self.env.company)
        self.assertEqual(self.guarantee.renewal_count, 0)
        self.assertFalse(self.guarantee.is_active)
        self.assertFalse(self.guarantee.release_date)

    def test_02_activate_release_workflow(self):
        self.assertTrue(self.guarantee.action_activate())
        self.assertEqual(self.guarantee.state, "active")
        self.assertTrue(self.guarantee.is_active)
        self.assertTrue(self.guarantee.action_release())
        self.assertEqual(self.guarantee.state, "released")
        self.assertFalse(self.guarantee.is_active)
        self.assertTrue(self.guarantee.release_date)

    def test_03_cancel_from_draft_and_active(self):
        draft = self.env["bank.guarantee"].create({
            "name": "BG-2026-002",
            "beneficiary_id": self.beneficiary.id,
            "amount": 5000.0,
            "issue_date": date(2026, 2, 1),
            "expiry_date": date(2027, 2, 1),
        })
        draft.action_cancel()
        self.assertEqual(draft.state, "cancelled")
        self.guarantee.action_activate()
        self.guarantee.action_cancel()
        self.assertEqual(self.guarantee.state, "cancelled")

    def test_04_invalid_transitions(self):
        with self.assertRaises(UserError):
            self.guarantee.action_release()
        self.guarantee.action_activate()
        with self.assertRaises(UserError):
            self.guarantee.action_activate()
        self.guarantee.action_release()
        with self.assertRaises(UserError):
            self.guarantee.action_cancel()

    def test_05_renewal_updates_expiry_and_count(self):
        self.guarantee.action_activate()
        renewal = self.env["bank.guarantee.renewal"].create({
            "guarantee_id": self.guarantee.id,
            "renewed_on": date(2026, 12, 15),
            "previous_expiry": date(2027, 1, 10),
            "new_expiry": date(2027, 7, 10),
            "fee": 150.0,
        })
        self.guarantee.invalidate_recordset()
        self.assertEqual(self.guarantee.expiry_date, date(2027, 7, 10))
        self.assertEqual(self.guarantee.renewal_count, 1)
        self.assertEqual(renewal.currency_id, self.guarantee.currency_id)

    def test_06_released_guarantee_cannot_be_renewed(self):
        self.guarantee.action_activate()
        self.guarantee.action_release()
        with self.assertRaises(UserError):
            self.env["bank.guarantee.renewal"].create({
                "guarantee_id": self.guarantee.id,
                "renewed_on": date(2027, 1, 5),
                "previous_expiry": date(2027, 1, 10),
                "new_expiry": date(2027, 6, 10),
            })

    def test_07_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["bank.guarantee"].create({
                "name": "BG-BAD-DATE",
                "beneficiary_id": self.beneficiary.id,
                "amount": 1000.0,
                "issue_date": date(2026, 6, 1),
                "expiry_date": date(2026, 5, 1),
            })
        with self.assertRaises(ValidationError):
            self.env["bank.guarantee"].create({
                "name": "BG-BAD-AMOUNT",
                "beneficiary_id": self.beneficiary.id,
                "amount": 0.0,
                "issue_date": date(2026, 3, 1),
                "expiry_date": date(2027, 3, 1),
            })
        self.guarantee.action_activate()
        self.guarantee.write({"release_date": False})
        with self.assertRaises(ValidationError):
            self.env["bank.guarantee.renewal"].create({
                "guarantee_id": self.guarantee.id,
                "renewed_on": date(2026, 11, 1),
                "previous_expiry": date(2027, 1, 10),
                "new_expiry": date(2026, 12, 1),
            })

    def test_08_company_isolation(self):
        foreign_partner = self.env["res.partner"].with_company(
            self.other_company).create({"name": "GuaranteeDesk Foreign"})
        foreign = self.env["bank.guarantee"].with_company(
            self.other_company).create({
            "name": "BG-FOREIGN-001",
            "beneficiary_id": foreign_partner.id,
            "amount": 7000.0,
            "issue_date": date(2026, 4, 1),
            "expiry_date": date(2027, 4, 1),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(self.guarantee.company_id, self.env.company)
