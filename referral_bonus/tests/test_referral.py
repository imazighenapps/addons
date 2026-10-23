# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReferral(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.campaign = cls.env["referral.campaign"].create({
            "name": "2026 Referral Programme",
            "bonus_on_hire": 500.0,
            "bonus_on_retention": 250.0,
            "probation_days": 90,
        })
        cls.referrer = cls.env["hr.employee"].create({"name": "Referrer One"})
        cls.job = cls.env["hr.job"].create({"name": "Field Technician"})

    def _case(self, name="Candidate"):
        return self.env["referral.case"].create({
            "campaign_id": self.campaign.id,
            "referrer_id": self.referrer.id,
            "candidate_name": name,
            "candidate_email": "cand@demo.test",
            "job_id": self.job.id,
        })

    def test_01_sequence(self):
        case = self._case()
        self.assertTrue(case.name.startswith("REF-"))
        self.assertEqual(case.state, "submitted")

    def test_02_hire_accrues_bonus(self):
        case = self._case()
        case.action_screening()
        self.assertEqual(case.state, "screening")
        emp = self.env["hr.employee"].create({
            "name": "New Hire", "date_start": date.today()})
        case.action_hire(emp.id)
        self.assertEqual(case.state, "hired")
        self.assertEqual(case.paid_amount, 500.0)

    def test_03_double_hire_blocked(self):
        case = self._case()
        emp = self.env["hr.employee"].create({"name": "Another Hire"})
        case.action_hire(emp.id)
        with self.assertRaises(UserError):
            case.action_hire(emp.id)

    def test_04_retention_bonus(self):
        case = self._case()
        emp = self.env["hr.employee"].create({
            "name": "Retained Hire", "date_start": date.today()})
        case.action_hire(emp.id)
        case.action_confirm_retention()
        self.assertEqual(case.state, "retained")
        self.assertEqual(case.paid_amount, 750.0)

    def test_05_retention_requires_hire(self):
        case = self._case()
        with self.assertRaises(UserError):
            case.action_confirm_retention()

    def test_06_campaign_stats_and_counter(self):
        case = self._case()
        emp = self.env["hr.employee"].create({
            "name": "Counted Hire", "date_start": date.today()})
        case.action_hire(emp.id)
        self.campaign.invalidate_recordset()
        self.assertEqual(self.campaign.hired_count, 1)
        self.assertEqual(self.campaign.total_paid, 500.0)
        self.referrer.invalidate_recordset()
        self.assertEqual(self.referrer.referrals_made, 1)
        self.job.invalidate_recordset()
        self.assertEqual(self.job.referral_count, 1)

    def test_07_reject_flow(self):
        case = self._case()
        case.action_reject("Candidate withdrew")
        self.assertEqual(case.state, "rejected")
        self.assertEqual(case.rejection_reason, "Candidate withdrew")
        self.assertEqual(case.paid_amount, 0.0)
