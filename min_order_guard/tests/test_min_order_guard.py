# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOrderMin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "OrderMin Other Company"})
        cls.rule = cls.env["order.min.rule"].create({
            "name": "OrderMin Test Threshold",
            "partner_name": "OrderMin Test Customer",
            "min_amount": 200.0,
            "min_quantity": 10,
        })

    def _exception(self, **values):
        defaults = {
            "rule_id": self.rule.id,
            "reference": "OrderMin Test Order SO-4410",
            "order_amount": 90.0,
            "order_quantity": 4,
        }
        defaults.update(values)
        return self.env["order.min.exception"].create(defaults)

    def test_01_exception_defaults(self):
        exception = self._exception()
        self.assertEqual(exception.state, "pending")
        self.assertEqual(exception.company_id, self.env.company)
        self.assertTrue(exception.name.startswith("Exception "))
        self.assertFalse(exception.reason)

    def test_02_shortfall_is_computed_and_stored(self):
        exception = self._exception()
        self.assertEqual(exception.shortfall, 110.0)
        below = self._exception(order_amount=240.0)
        self.assertEqual(below.shortfall, 0.0)

    def test_03_allowing_requires_a_written_reason(self):
        exception = self._exception()
        with self.assertRaises(UserError):
            exception.action_allow()
        exception.write({"reason": "OrderMin Test regular customer"})
        self.assertTrue(exception.action_allow())
        self.assertEqual(exception.state, "allowed")
        self.assertEqual(exception.decided_by, self.env.user)
        self.assertTrue(exception.decided_on)

    def test_04_refusal_needs_no_reason(self):
        exception = self._exception()
        self.assertTrue(exception.action_refuse())
        self.assertEqual(exception.state, "refused")
        self.assertTrue(exception.decided_by)

    def test_05_double_decision_is_refused(self):
        exception = self._exception()
        exception.action_refuse()
        with self.assertRaises(UserError):
            exception.action_refuse()
        with self.assertRaises(UserError):
            exception.action_allow()

    def test_06_rule_needs_a_minimum(self):
        with self.assertRaises(ValidationError):
            self.env["order.min.rule"].create({
                "name": "OrderMin Test Empty Rule",
                "partner_name": "OrderMin Test Second Customer",
                "min_amount": 0.0,
                "min_quantity": 0,
            })
        with self.assertRaises(ValidationError):
            self._exception(order_amount=-5.0)

    def test_07_rule_counter(self):
        self._exception()
        decided = self._exception(reference="OrderMin Test Order SO-4411")
        decided.write({"reason": "OrderMin Test logistics fee"})
        decided.action_allow()
        self.rule.invalidate_recordset()
        self.assertEqual(self.rule.exception_count, 2)

    def test_08_pending_filter(self):
        exception = self._exception(
            reference="OrderMin Test Order SO-4412")
        found = self.env["order.min.exception"].search([
            ("state", "=", "pending"),
            ("rule_id", "=", self.rule.id)])
        self.assertIn(exception, found)

    def test_09_company_isolation(self):
        foreign = self._exception(
            company_id=self.other_company.id).sudo()
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._exception(reference="OrderMin Test Order SO-4413")
        self.assertEqual(local.company_id, self.env.company)
