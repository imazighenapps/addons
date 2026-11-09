# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTaxCalendar(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

    def _rule(self, name, frequency="monthly", tax_type="vat", **kwargs):
        values = {
            "name": name,
            "tax_type": tax_type,
            "frequency": frequency,
        }
        values.update(kwargs)
        return self.env["tax.rule"].create(values)

    def _generate(self, rules, year=2099):
        wizard = self.env["tax.calendar.wizard"].create({
            "year": year,
            "rule_ids": [(6, 0, rules.ids)],
        })
        return wizard.action_generate()

    def _deadline(self, rule, start, end, due):
        return self.env["tax.deadline"].create({
            "name": "%s %s" % (rule.name, start),
            "rule_id": rule.id,
            "period_start": start,
            "period_end": end,
            "due_date": due,
        })

    def _deadlines(self, rule):
        return self.env["tax.deadline"].search(
            [("rule_id", "=", rule.id)], order="period_start")

    def test_01_monthly_rule_generates_twelve_deadlines(self):
        rule = self._rule("VAT Monthly Test")
        self.assertTrue(self._generate(rule))
        deadlines = self._deadlines(rule)
        self.assertEqual(len(deadlines), 12)
        self.assertEqual(deadlines[0].period_start, date(2099, 1, 1))
        self.assertEqual(deadlines[0].period_end, date(2099, 1, 31))
        self.assertEqual(deadlines[-1].period_start, date(2099, 12, 1))
        self.assertEqual(deadlines[-1].period_end, date(2099, 12, 31))
        self.assertEqual(set(deadlines.mapped("state")), {"upcoming"})

    def test_02_quarterly_rule_generates_four_periods(self):
        rule = self._rule(
            "Corporate Quarterly Test", frequency="quarterly",
            tax_type="corporate")
        self._generate(rule)
        deadlines = self._deadlines(rule)
        self.assertEqual(len(deadlines), 4)
        periods = [(item.period_start, item.period_end) for item in deadlines]
        self.assertEqual(periods, [
            (date(2099, 1, 1), date(2099, 3, 31)),
            (date(2099, 4, 1), date(2099, 6, 30)),
            (date(2099, 7, 1), date(2099, 9, 30)),
            (date(2099, 10, 1), date(2099, 12, 31)),
        ])

    def test_03_regeneration_does_not_duplicate(self):
        rule = self._rule("Payroll Monthly Test", tax_type="payroll")
        self._generate(rule)
        self._generate(rule)
        deadlines = self._deadlines(rule)
        self.assertEqual(len(deadlines), 12)
        self.assertEqual(len(set(deadlines.mapped("period_start"))), 12)

    def test_04_due_date_is_period_end_plus_due_day(self):
        rule = self._rule("VAT Due Day Test", due_day=10)
        self._generate(rule)
        first = self._deadlines(rule)[:1]
        self.assertEqual(first.period_end, date(2099, 1, 31))
        self.assertEqual(first.due_date, date(2099, 2, 10))
        self.assertEqual(first.due_date, first.period_end + timedelta(days=10))

    def test_05_action_done_and_reset(self):
        rule = self._rule("Withholding Done Test", tax_type="withholding")
        deadline = self._deadline(
            rule, date(2099, 1, 1), date(2099, 1, 31), date(2099, 2, 15))
        self.assertTrue(deadline.action_done())
        self.assertEqual(deadline.state, "done")
        self.assertEqual(deadline.done_date,
                         fields.Date.context_today(deadline))
        with self.assertRaises(UserError):
            deadline.action_done()
        self.assertTrue(deadline.action_reset())
        self.assertEqual(deadline.state, "upcoming")
        self.assertFalse(deadline.done_date)
        with self.assertRaises(UserError):
            deadline.action_reset()

    def test_06_is_late_flag(self):
        rule = self._rule("VAT Late Flag Test")
        past = self._deadline(
            rule, date(1999, 12, 1), date(1999, 12, 31), date(2000, 1, 15))
        future = self._deadline(
            rule, date(2099, 1, 1), date(2099, 1, 31), date(2099, 2, 15))
        self.assertTrue(past.is_late)
        self.assertLess(past.days_left, 0)
        self.assertFalse(future.is_late)
        self.assertGreater(future.days_left, 0)
        past.action_done()
        self.assertFalse(past.is_late)

    def test_07_period_end_before_period_start_is_refused(self):
        rule = self._rule("VAT Bad Period Test")
        with self.assertRaises(ValidationError):
            self._deadline(
                rule, date(2099, 12, 31), date(2099, 1, 1),
                date(2099, 1, 15))

    def test_08_company_isolation(self):
        other_company = self.env["res.company"].create({
            "name": "TaxCalendar Other Company"})
        self.env.user.write({"company_ids": [(4, other_company.id)]})
        rule_mine = self._rule("VAT Isolation Mine")
        self._generate(rule_mine)
        rule_theirs = self.env["tax.rule"].create({
            "name": "VAT Isolation Theirs",
            "tax_type": "vat",
            "frequency": "monthly",
            "company_id": other_company.id,
        })
        wizard = self.env["tax.calendar.wizard"].create({
            "year": 2099,
            "rule_ids": [(6, 0, rule_theirs.ids)],
        })
        wizard.action_generate()
        theirs = self.env["tax.deadline"].search(
            [("rule_id", "=", rule_theirs.id)])
        self.assertEqual(len(theirs), 12)
        self.assertEqual(theirs[0].company_id, other_company)
        group_user = self.env.ref("tax_calendar_pro.group_taxcalendarp_user")
        reader = self.env["res.users"].create({
            "name": "Tax Calendar Reader",
            "login": "tax_calendar_reader",
            "email": "tax.calendar.reader@example.com",
            "company_id": self.company.id,
            "company_ids": [(6, 0, [self.company.id])],
            "groups_id": [(6, 0, [group_user.id])],
        })
        visible = self.env["tax.deadline"].with_user(reader).search(
            [("rule_id", "=", rule_theirs.id)])
        self.assertFalse(visible)
        mine = self.env["tax.deadline"].with_user(reader).search(
            [("rule_id", "=", rule_mine.id)])
        self.assertEqual(len(mine), 12)
