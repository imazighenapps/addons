# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRoundOff(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "RoundOff Other Company"})
        cls.currency = cls.env.company.currency_id
        cls.rule = cls.env["round.rule"].create({
            "name": "RoundOff Penny",
            "max_amount": 0.05,
            "reason": "Rounding difference",
            "currency_id": cls.currency.id,
        })

    def _writeoff(self, rule=None, **values):
        defaults = {
            "rule_id": (rule or self.rule).id,
            "source_ref": "INV/2026/0001",
            "amount": 0.02,
            "writeoff_on": date(2026, 2, 14),
        }
        defaults.update(values)
        return self.env["round.writeoff"].create(defaults)

    def test_01_writeoff_defaults(self):
        writeoff = self._writeoff()
        self.assertEqual(writeoff.state, "draft")
        self.assertEqual(writeoff.company_id, self.env.company)
        self.assertTrue(writeoff.name.startswith("Write-Off "))
        self.assertFalse(writeoff.posted_on)

    def test_02_post_stamps_date(self):
        writeoff = self._writeoff()
        self.assertTrue(writeoff.action_post())
        self.assertEqual(writeoff.state, "posted")
        self.assertTrue(writeoff.posted_on)

    def test_03_double_post_is_refused(self):
        writeoff = self._writeoff(source_ref="INV/2026/0002")
        writeoff.action_post()
        with self.assertRaises(ValidationError):
            writeoff.action_post()

    def test_04_amount_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._writeoff(amount=0.0)
        with self.assertRaises(ValidationError):
            self._writeoff(amount=-0.01)

    def test_05_amount_above_limit_is_refused(self):
        with self.assertRaises(ValidationError):
            self._writeoff(amount=0.10, source_ref="INV/2026/0003")

    def test_06_rule_counters(self):
        posted = self._writeoff(amount=0.03, source_ref="INV/2026/0004")
        draft = self._writeoff(amount=0.02, source_ref="INV/2026/0005",
                               writeoff_on=date(2026, 3, 3))
        posted.action_post()
        self.rule.invalidate_recordset()
        self.assertEqual(self.rule.writeoff_count, 2)
        self.assertAlmostEqual(self.rule.cleared_amount, 0.03, places=2)
        self.assertTrue(draft)

    def test_07_rule_max_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.env["round.rule"].create({
                "name": "RoundOff Bad",
                "max_amount": 0.0,
                "reason": "Bad rule",
            })

    def test_08_company_isolation(self):
        foreign_rule = self.env["round.rule"].with_company(
            self.other_company).sudo().create({
            "name": "RoundOff Foreign Rule",
            "max_amount": 0.10,
            "reason": "Foreign rounding",
            "currency_id": self.currency.id,
            "company_id": self.other_company.id,
        })
        foreign = self.env["round.writeoff"].with_company(
            self.other_company).sudo().create({
            "rule_id": foreign_rule.id,
            "source_ref": "FOR/2026/0001",
            "amount": 0.04,
            "writeoff_on": date(2026, 4, 9),
            "company_id": self.other_company.id,
        })
        local = self._writeoff(source_ref="INV/2026/0006",
                               writeoff_on=date(2026, 5, 20))
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(local.company_id, self.env.company)
