# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMarginGuard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "MarginGuard Other Company"})
        cls.rule = cls.env["margin.rule"].create({
            "name": "MarginGuard Test Floor",
            "scope_type": "product",
            "scope_ref": "MarginGuard Test Product",
            "discount_floor": 10.0,
            "margin_floor": 22.0,
        })

    def _check(self, rule=None, **values):
        defaults = {
            "rule_id": (rule or self.rule).id,
            "reference": "MarginGuard Test Line LX-1",
            "requested_discount": 18.0,
            "requested_margin": 15.0,
            "checked_on": "2026-08-06",
        }
        defaults.update(values)
        return self.env["margin.check"].create(defaults)

    def test_01_check_defaults(self):
        check = self._check()
        self.assertEqual(check.state, "pending")
        self.assertEqual(check.company_id, self.env.company)
        self.assertTrue(check.name.startswith("Check "))

    def test_02_rule_needs_a_floor(self):
        with self.assertRaises(ValidationError):
            self.env["margin.rule"].create({
                "name": "MarginGuard Test Empty Rule",
                "scope_type": "product",
                "scope_ref": "MarginGuard Test Product",
                "discount_floor": 0.0,
                "margin_floor": 0.0,
            })

    def test_03_floors_stay_in_range(self):
        with self.assertRaises(ValidationError):
            self._check(rule=self.env["margin.rule"].create({
                "name": "MarginGuard Test Wide Floor",
                "scope_type": "global",
                "discount_floor": 120.0,
                "margin_floor": 5.0,
            }))

    def test_04_requested_values_stay_in_range(self):
        with self.assertRaises(ValidationError):
            self._check(requested_discount=110.0)
        with self.assertRaises(ValidationError):
            self._check(requested_margin=-2.0)

    def test_05_approval_stamps_the_decision(self):
        check = self._check()
        self.assertTrue(check.action_approve())
        self.assertEqual(check.state, "approved")
        self.assertEqual(check.decided_by, self.env.user)
        self.assertTrue(check.decided_on)

    def test_06_double_decision_is_refused(self):
        check = self._check()
        check.action_reject()
        self.assertEqual(check.state, "rejected")
        with self.assertRaises(UserError):
            check.action_reject()
        with self.assertRaises(UserError):
            check.action_approve()

    def test_07_rule_counter(self):
        pending = self._check()
        closed = self._check(reference="MarginGuard Test Line LX-2")
        closed.action_approve()
        self.rule.invalidate_recordset()
        self.assertEqual(self.rule.check_count, 2)
        self.assertTrue(pending)

    def test_08_pending_filter(self):
        check = self._check(reference="MarginGuard Test Line LX-3")
        found = self.env["margin.check"].search([
            ("state", "=", "pending"),
            ("rule_id", "=", self.rule.id)])
        self.assertIn(check, found)
        check.action_approve()
        found = self.env["margin.check"].search([
            ("state", "=", "rejected"),
            ("rule_id", "=", self.rule.id)])
        self.assertNotIn(check, found)

    def test_09_company_isolation(self):
        foreign_rule = self.env["margin.rule"].with_company(
            self.other_company).sudo().create({
            "name": "MarginGuard Test Foreign Floor",
            "scope_type": "global",
            "discount_floor": 5.0,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign_rule.company_id, self.other_company)
        self.assertNotEqual(foreign_rule.company_id, self.env.company)
        foreign = self._check(
            rule=foreign_rule, company_id=self.other_company.id).sudo()
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._check()
        self.assertEqual(local.company_id, self.env.company)
