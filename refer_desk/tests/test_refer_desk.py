# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReferBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ReferBook Other Company"})

    def _code(self, **values):
        defaults = {
            "name": "RB-ADV-001",
            "advocate_name": "ReferBook Advocate A",
        }
        defaults.update(values)
        return self.env["refer.code"].create(defaults)

    def _referral(self, code, **values):
        defaults = {
            "name": "ReferBook Referral",
            "code_id": code.id,
            "referred_name": "ReferBook Friend A",
            "referred_on": date(2026, 7, 10),
            "order_amount": 200.0,
            "reward_amount": 20.0,
        }
        defaults.update(values)
        return self.env["refer.referral"].create(defaults)

    def test_01_code_defaults(self):
        code = self._code()
        self.assertEqual(code.state, "active")
        self.assertEqual(code.company_id, self.env.company)
        self.assertEqual(code.referral_count, 0)
        self.assertEqual(code.total_reward, 0.0)

    def test_02_credit_referral_updates_totals(self):
        code = self._code()
        ref = self._referral(code)
        self.assertTrue(ref.action_credit())
        self.assertEqual(ref.state, "credited")
        self.assertTrue(ref.credited_on)
        code.invalidate_recordset()
        self.assertEqual(code.referral_count, 1)
        self.assertEqual(code.credited_count, 1)
        self.assertEqual(code.total_reward, 20.0)

    def test_03_cancel_referral(self):
        code = self._code(name="RB-ADV-002", advocate_name="ReferBook Advocate B")
        ref = self._referral(code, referred_name="ReferBook Friend B")
        self.assertTrue(ref.action_cancel())
        self.assertEqual(ref.state, "cancelled")
        with self.assertRaises(UserError):
            ref.action_credit()

    def test_04_cannot_credit_twice(self):
        code = self._code(name="RB-ADV-003", advocate_name="ReferBook Advocate C")
        ref = self._referral(code, referred_name="ReferBook Friend C")
        ref.action_credit()
        with self.assertRaises(UserError):
            ref.action_credit()

    def test_05_duplicate_code_is_refused(self):
        self._code(name="RB-ADV-004", advocate_name="ReferBook Advocate D")
        with self.assertRaises(ValidationError):
            self._code(name="RB-ADV-004", advocate_name="ReferBook Advocate D2")

    def test_06_negative_amounts_are_refused(self):
        code = self._code(name="RB-ADV-005", advocate_name="ReferBook Advocate E")
        with self.assertRaises(ValidationError):
            self._referral(code, order_amount=-1.0)
        with self.assertRaises(ValidationError):
            self._referral(code, reward_amount=-5.0,
                           referred_name="ReferBook Friend E2")

    def test_07_close_and_reopen_code(self):
        code = self._code(name="RB-ADV-006", advocate_name="ReferBook Advocate F")
        self.assertTrue(code.action_close())
        self.assertEqual(code.state, "closed")
        with self.assertRaises(UserError):
            code.action_close()
        self.assertTrue(code.action_reopen())
        self.assertEqual(code.state, "active")

    def test_08_cannot_credit_on_closed_code(self):
        code = self._code(name="RB-ADV-007", advocate_name="ReferBook Advocate G")
        ref = self._referral(code, referred_name="ReferBook Friend G",
                             referred_on=date(2026, 8, 5))
        code.action_close()
        with self.assertRaises(UserError):
            ref.action_credit()

    def test_09_company_isolation(self):
        foreign = self.env["refer.code"].with_company(
            self.other_company).sudo().create({
            "name": "RB-FOR-001",
            "advocate_name": "ReferBook Foreign Advocate",
            "company_id": self.other_company.id,
        })
        local = self._code(name="RB-LOC-001", advocate_name="ReferBook Local Advocate")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
