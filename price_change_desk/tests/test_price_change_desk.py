# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPriceShift(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "PriceShift Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "PriceShift Test Customer"})
        cls.partner2 = cls.env["res.partner"].create({
            "name": "PriceShift Test Second Customer"})

    def _shift(self, **values):
        defaults = {
            "description": "PriceShift Test Catalogue Increase",
            "change_type": "increase",
            "percent": 4.0,
            "effective_on": fields.Date.to_date("2027-01-04"),
        }
        defaults.update(values)
        return self.env["price.shift"].create(defaults)

    def _line(self, shift, partner=None, price=100.0):
        return self.env["price.shift.line"].create({
            "shift_id": shift.id,
            "partner_id": (partner or self.partner).id,
            "current_price": price,
        })

    def _scheduled(self, **values):
        shift = self._shift(**values)
        self._line(shift)
        self._line(shift, partner=self.partner2)
        shift.action_schedule()
        return shift

    def test_01_shift_defaults(self):
        shift = self._shift()
        self.assertTrue(shift.name.startswith("PSC/"))
        self.assertEqual(shift.state, "draft")
        self.assertEqual(shift.change_type, "increase")
        self.assertEqual(shift.percent, 4.0)
        self.assertEqual(shift.customer_count, 0)
        self.assertFalse(shift.applied_on)
        self.assertEqual(shift.company_id, self.env.company)
        self.assertEqual(
            shift.company_id.currency_id, self.env.company.currency_id)

    def test_02_increase_computes_the_new_price(self):
        shift = self._shift(percent=10.0)
        line = self._line(shift, price=100.0)
        self.assertAlmostEqual(line.new_price, 110.0, places=2)
        zero = self._line(shift, price=0.0)
        self.assertAlmostEqual(zero.new_price, 0.0, places=2)

    def test_03_decrease_computes_the_new_price(self):
        shift = self._shift(change_type="decrease", percent=25.0)
        line = self._line(shift, price=80.0)
        self.assertAlmostEqual(line.new_price, 60.0, places=2)
        with self.assertRaises(ValidationError):
            self._line(shift, price=-5.0)

    def test_04_percent_bounds_are_refused(self):
        with self.assertRaises(ValidationError):
            self._shift(percent=0.0)
        with self.assertRaises(ValidationError):
            self._shift(percent=-2.0)
        with self.assertRaises(ValidationError):
            self._shift(percent=101.0)
        self.assertEqual(self._shift(percent=100.0).percent, 100.0)

    def test_05_schedule_requires_lines(self):
        empty = self._shift()
        with self.assertRaises(UserError):
            empty.action_schedule()
        self.assertEqual(empty.state, "draft")
        scheduled = self._scheduled()
        self.assertEqual(scheduled.state, "scheduled")
        self.assertEqual(scheduled.customer_count, 2)
        with self.assertRaises(UserError):
            scheduled.action_schedule()

    def test_06_rule_is_locked_once_scheduled(self):
        scheduled = self._scheduled()
        with self.assertRaises(UserError):
            scheduled.write({"percent": 7.0})
        with self.assertRaises(UserError):
            scheduled.write({"effective_on":
                             fields.Date.to_date("2027-02-01")})
        self.assertEqual(scheduled.percent, 4.0)
        draft = self._shift()
        draft.write({"percent": 9.0})
        self.assertEqual(draft.percent, 9.0)

    def test_07_apply_stamps_and_freezes(self):
        shift = self._scheduled()
        line = shift.line_ids[0]
        self.assertTrue(shift.action_apply())
        self.assertEqual(shift.state, "applied")
        self.assertTrue(shift.applied_on)
        with self.assertRaises(UserError):
            shift.action_apply()
        with self.assertRaises(UserError):
            self._line(shift, partner=self.partner2)
        with self.assertRaises(UserError):
            line.write({"current_price": 250.0})
        self.assertAlmostEqual(line.current_price, 100.0, places=2)

    def test_08_cancel_keeps_the_trace(self):
        shift = self._scheduled()
        self.assertTrue(shift.action_cancel())
        self.assertEqual(shift.state, "cancelled")
        self.assertEqual(shift.customer_count, 2)
        with self.assertRaises(UserError):
            shift.action_apply()
        with self.assertRaises(UserError):
            shift.action_cancel()
        out_of_cycle = self._scheduled()
        out_of_cycle.action_apply()
        with self.assertRaises(UserError):
            out_of_cycle.action_cancel()

    def test_09_company_isolation(self):
        foreign = self.env["price.shift"].with_company(
            self.other_company).sudo().create({
            "description": "PriceShift Test Foreign Increase",
            "effective_on": fields.Date.to_date("2027-01-04"),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._shift()
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
        self.assertEqual(local.company_id.currency_id,
                         self.env.company.currency_id)

    def test_10_search_filters(self):
        scheduled = self._scheduled()
        applied = self._shift()
        self._line(applied)
        applied.action_schedule()
        applied.action_apply()
        shifts = self.env["price.shift"]
        self.assertIn(scheduled, shifts.search([
            ("state", "=", "scheduled")]))
        self.assertIn(scheduled, shifts.search([
            ("state", "=", "scheduled"), ("customer_count", ">", 0)]))
        self.assertIn(applied, shifts.search([
            ("effective_on", ">=", "2026-01-01")]))
        lines = self.env["price.shift.line"].search([
            ("shift_id.state", "=", "applied")])
        self.assertTrue(lines)
        self.assertTrue(all(line.new_price for line in lines))
