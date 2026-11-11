# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRecoverBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "RecoverBook Other Company"})
        cls.currency = cls.env.company.currency_id

    def _claim(self, **values):
        defaults = {
            "name": "RecoverBook Carrier Refund",
            "partner_name": "Carrier Express",
            "origin_ref": "SHIP/2026/001",
            "claim_kind": "refund",
            "amount_expected": 120.0,
            "currency_id": self.currency.id,
            "due_on": date(2026, 3, 15),
        }
        defaults.update(values)
        return self.env["recover.claim"].create(defaults)

    def test_01_claim_defaults(self):
        claim = self._claim()
        self.assertEqual(claim.state, "open")
        self.assertEqual(claim.company_id, self.env.company)
        self.assertEqual(claim.amount_recovered, 0.0)
        self.assertFalse(claim.recovered_on)

    def test_02_recover_sets_amount_and_date(self):
        claim = self._claim(name="RecoverBook Rebate")
        self.assertTrue(claim.action_recover())
        self.assertEqual(claim.state, "recovered")
        self.assertAlmostEqual(claim.amount_recovered, 120.0, places=2)
        self.assertTrue(claim.recovered_on)

    def test_03_write_off_open_claim(self):
        claim = self._claim(name="RecoverBook Write Off")
        self.assertTrue(claim.action_write_off())
        self.assertEqual(claim.state, "written_off")

    def test_04_double_recover_is_refused(self):
        claim = self._claim(name="RecoverBook Double")
        claim.action_recover()
        with self.assertRaises(ValidationError):
            claim.action_recover()

    def test_05_amount_rules(self):
        with self.assertRaises(ValidationError):
            self._claim(name="RecoverBook Zero", amount_expected=0.0)
        with self.assertRaises(ValidationError):
            self._claim(name="RecoverBook Neg", amount_recovered=-1.0)
        with self.assertRaises(ValidationError):
            self._claim(name="RecoverBook Over", amount_expected=50.0,
                        amount_recovered=60.0)

    def test_06_chase_actions_count(self):
        claim = self._claim(name="RecoverBook Chase")
        self.env["recover.action"].create({
            "claim_id": claim.id,
            "action_on": date(2026, 4, 2),
            "channel": "email",
            "summary": "First reminder sent.",
        })
        self.env["recover.action"].create({
            "claim_id": claim.id,
            "action_on": date(2026, 4, 10),
            "channel": "phone",
            "summary": "Called the supplier.",
        })
        claim.invalidate_recordset()
        self.assertEqual(claim.action_count, 2)

    def test_07_chase_summary_required(self):
        claim = self._claim(name="RecoverBook Bad Action")
        with self.assertRaises(ValidationError):
            self.env["recover.action"].create({
                "claim_id": claim.id,
                "action_on": date(2026, 5, 6),
                "summary": "   ",
            })

    def test_08_company_isolation(self):
        foreign = self.env["recover.claim"].with_company(
            self.other_company).sudo().create({
            "name": "RecoverBook Foreign Claim",
            "partner_name": "Foreign Vendor",
            "claim_kind": "rebate",
            "amount_expected": 80.0,
            "currency_id": self.currency.id,
            "due_on": date(2026, 6, 1),
            "company_id": self.other_company.id,
        })
        local = self._claim(name="RecoverBook Local Claim",
                            due_on=date(2026, 7, 1))
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(local.company_id, self.env.company)
