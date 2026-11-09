# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestQualityClaimPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "ClaimDesk Test Customer", "is_company": True})
        cls.supplier = cls.env["res.partner"].create({
            "name": "ClaimDesk Test Supplier", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "ClaimDesk Test Component", "type": "consu"})

    def _claim(self, **kwargs):
        values = {
            "name": "Claim TC-001",
            "claim_type": "customer",
            "partner_id": self.partner.id,
            "product_id": self.product.id,
            "quantity": 2.0,
            "defect_code": "dimensional",
            "severity": "major",
            "date_claim": date(2026, 3, 2),
        }
        values.update(kwargs)
        return self.env["quality.claim"].create(values)

    def _action(self, claim, name="Replace the defective lot"):
        return self.env["quality.claim.action"].create({
            "claim_id": claim.id,
            "name": name,
            "user_id": self.env.user.id,
        })

    def _in_action(self, root_cause="Wrong torque on the assembly line"):
        claim = self._claim()
        claim.action_open()
        claim.action_investigate()
        claim.write({"root_cause": root_cause})
        claim.action_plan()
        return claim

    def test_01_open_claim(self):
        claim = self._claim()
        self.assertEqual(claim.state, "draft")
        self.assertTrue(claim.action_open())
        self.assertEqual(claim.state, "open")
        with self.assertRaises(UserError):
            claim.action_open()
        self.assertEqual(claim.state, "open")
        self.assertTrue(claim.action_investigate())
        self.assertEqual(claim.state, "investigation")

    def test_02_plan_requires_a_root_cause(self):
        claim = self._claim()
        claim.action_open()
        claim.action_investigate()
        self.assertEqual(claim.state, "investigation")
        with self.assertRaises(UserError):
            claim.action_plan()
        self.assertEqual(claim.state, "investigation")
        claim.write({"root_cause": "   "})
        with self.assertRaises(UserError):
            claim.action_plan()
        self.assertEqual(claim.state, "investigation")

    def test_03_plan_with_a_root_cause(self):
        claim = self._claim()
        claim.action_open()
        claim.action_investigate()
        claim.write({"root_cause": "Wrong torque on the assembly line."})
        self.assertTrue(claim.action_plan())
        self.assertEqual(claim.state, "action")

    def test_04_action_done_updates_the_counters(self):
        claim = self._in_action()
        action = self._action(claim)
        claim.invalidate_recordset()
        self.assertEqual(claim.action_count, 1)
        self.assertEqual(claim.action_done_count, 0)
        self.assertTrue(action.action_done())
        self.assertEqual(action.state, "done")
        self.assertTrue(action.done_date)
        claim.invalidate_recordset()
        self.assertEqual(claim.action_done_count, 1)
        self.assertTrue(action.action_reopen())
        self.assertEqual(action.state, "todo")
        self.assertFalse(action.done_date)
        claim.invalidate_recordset()
        self.assertEqual(claim.action_done_count, 0)

    def test_05_close_refused_while_an_action_is_open(self):
        claim = self._in_action()
        self._action(claim)
        self._action(claim, name="Update the work instruction")
        with self.assertRaises(UserError):
            claim.action_close()
        self.assertEqual(claim.state, "action")

    def test_06_close_when_every_action_is_done(self):
        claim = self._in_action()
        first = self._action(claim)
        second = self._action(claim, name="Update the work instruction")
        first.action_done()
        second.action_done()
        claim.invalidate_recordset()
        self.assertEqual(claim.action_done_count, 2)
        self.assertEqual(claim.action_count, 2)
        self.assertTrue(claim.action_close())
        self.assertEqual(claim.state, "done")

    def test_07_refuse_a_claim(self):
        claim = self._claim()
        self.assertTrue(claim.action_refuse())
        self.assertEqual(claim.state, "refused")
        self.assertTrue(claim.action_reset())
        self.assertEqual(claim.state, "draft")
        closed = self._in_action()
        done_action = self._action(closed)
        done_action.action_done()
        closed.action_close()
        self.assertEqual(closed.state, "done")
        with self.assertRaises(UserError):
            closed.action_refuse()
        self.assertEqual(closed.state, "done")

    def test_08_company_isolation(self):
        other = self.env["res.company"].create({
            "name": "ClaimDesk Other Company"})
        own = self._claim()
        foreign = self._claim(company_id=other.id)
        self.assertEqual(own.company_id, self.env.company)
        self.assertEqual(foreign.company_id, other)
        self.assertNotEqual(own.company_id, foreign.company_id)
        visible = self.env["quality.claim"].search([
            ("id", "in", (own | foreign).ids),
            ("company_id", "=", self.env.company.id),
        ])
        self.assertEqual(visible, own)
        self.assertNotIn(foreign, visible)
        with self.assertRaises(ValidationError):
            self._claim(quantity=0.0)
