# -*- coding: utf-8 -*-
from datetime import date

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHoldDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "HoldDesk Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "HoldDesk Test Customer"})
        cls.reason_credit = cls.env["hold.desk.reason"].create({
            "name": "HoldDesk Test Credit Freeze",
            "code": "HD-CRED",
            "sequence": 10,
        })
        cls.reason_stock = cls.env["hold.desk.reason"].create({
            "name": "HoldDesk Test Stock Shortage",
            "code": "HD-STCK",
            "sequence": 20,
        })

    def _hold(self, **values):
        defaults = {
            "reason_id": self.reason_credit.id,
            "document": "HoldDesk Test Order SO-1",
            "partner_id": self.partner.id,
            "amount": 4800.0,
            "hold_on": date(2026, 10, 12),
        }
        defaults.update(values)
        return self.env["hold.desk.request"].create(defaults)

    def _held(self, **values):
        hold = self._hold(**values)
        hold.action_hold()
        return hold

    def test_01_hold_defaults(self):
        hold = self._hold()
        self.assertTrue(hold.name.startswith("HDS/"))
        self.assertEqual(hold.state, "draft")
        self.assertEqual(hold.company_id, self.env.company)
        self.assertEqual(hold.amount, 4800.0)
        self.assertEqual(hold.hold_on, date(2026, 10, 12))
        self.assertFalse(hold.release_on)
        self.assertFalse(hold.released_by)
        self.assertEqual(hold.hold_days, 0)
        self.assertEqual(hold.currency_id, self.env.company.currency_id)

    def test_02_place_on_hold(self):
        hold = self._hold()
        self.assertTrue(hold.action_hold())
        self.assertEqual(hold.state, "hold")
        self.assertEqual(hold.hold_on, date(2026, 10, 12))
        self.assertTrue(hold.message_ids)
        with self.assertRaises(UserError):
            hold.action_hold()

    def test_03_release_stamps_the_trace(self):
        hold = self._held()
        self.assertTrue(hold.action_release())
        self.assertEqual(hold.state, "released")
        self.assertEqual(hold.release_on,
                         fields.Date.context_today(hold))
        self.assertEqual(hold.released_by, self.env.user)
        self.assertEqual(hold.hold_days,
                         (hold.release_on - hold.hold_on).days)

    def test_04_release_requires_being_on_hold(self):
        with self.assertRaises(UserError):
            self._hold().action_release()
        released = self._held()
        released.action_release()
        with self.assertRaises(UserError):
            released.action_release()
        self.assertEqual(released.state, "released")

    def test_05_abandon_and_abandoned_rules(self):
        draft = self._hold()
        self.assertTrue(draft.action_abandon())
        self.assertEqual(draft.state, "abandoned")
        on_hold = self._held(reason_id=self.reason_stock.id)
        self.assertTrue(on_hold.action_abandon())
        self.assertEqual(on_hold.state, "abandoned")
        with self.assertRaises(UserError):
            draft.action_release()
        with self.assertRaises(UserError):
            draft.action_abandon()

    def test_06_negative_amount_is_refused(self):
        with self.assertRaises(ValidationError):
            self._hold(amount=-1.0)
        self.assertEqual(
            self._hold(amount=0.0).amount, 0.0)

    def test_07_release_before_hold_date_is_refused(self):
        with self.assertRaises(ValidationError):
            self._hold(state="released", release_on=date(2026, 10, 2))
        hold = self._held()
        with self.assertRaises(ValidationError):
            hold.write({"release_on": date(2026, 10, 2)})

    def test_08_reason_counters(self):
        active = self._held()
        closed = self._held(document="HoldDesk Test Order SO-2",
                            reason_id=self.reason_stock.id)
        closed.action_release()
        self.reason_credit.invalidate_recordset()
        self.reason_stock.invalidate_recordset()
        self.assertEqual(self.reason_credit.request_count, 1)
        self.assertEqual(self.reason_credit.open_count, 1)
        self.assertEqual(self.reason_stock.request_count, 1)
        self.assertEqual(self.reason_stock.open_count, 0)
        self.assertTrue(active)

    def test_09_company_isolation(self):
        foreign_reason = self.env["hold.desk.reason"].with_company(
            self.other_company).sudo().create({
            "name": "HoldDesk Test Foreign Reason",
            "code": "HD-FOR",
        })
        self.assertEqual(foreign_reason.company_id, self.other_company)
        foreign = self.env["hold.desk.request"].with_company(
            self.other_company).sudo().create({
            "reason_id": foreign_reason.id,
            "document": "HoldDesk Test Order SO-FOR",
            "hold_on": date(2026, 10, 12),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._hold()
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)

    def test_10_search_filters_and_puts_together(self):
        on_hold = self._held()
        released = self._held(document="HoldDesk Test Order SO-3",
                              reason_id=self.reason_stock.id)
        released.action_release()
        self.assertIn(on_hold, self.env["hold.desk.request"].search(
            [("state", "=", "hold")]))
        self.assertIn(released, self.env["hold.desk.request"].search(
            [("state", "=", "released")]))
        self.assertIn(self.reason_credit,
                      self.env["hold.desk.reason"].search(
            [("open_count", ">", 0)]))
        found = self.env["hold.desk.request"].search([
            ("reason_id", "=", self.reason_credit.id)])
        self.assertIn(on_hold, found)
        self.assertNotIn(released, found)
