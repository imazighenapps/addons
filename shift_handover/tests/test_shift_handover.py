# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestShiftHandover(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({
            "name": "ShiftHandover Test Operator",
        })
        cls.department = cls.env["hr.department"].create({
            "name": "ShiftHandover Test Production",
        })

    def _handover(self, **kwargs):
        values = {
            "responsible_id": self.employee.id,
            "department_id": self.department.id,
            "shift": "morning",
        }
        values.update(kwargs)
        return self.env["shift.handover"].create(values)

    def _line(self, handover, **kwargs):
        values = {
            "handover_id": handover.id,
            "description": "Check the line before the next shift",
        }
        values.update(kwargs)
        return self.env["shift.handover.line"].create(values)

    def test_01_done_closes_the_handover(self):
        handover = self._handover(name="Handover 01")
        self._line(handover, description="Forklift battery on charge")
        self.assertEqual(handover.state, "draft")
        self.assertTrue(handover.action_done())
        self.assertEqual(handover.state, "done")
        with self.assertRaises(UserError):
            handover.action_done()

    def test_02_done_without_item_is_refused(self):
        handover = self._handover(name="Handover 02")
        self.assertFalse(handover.line_ids)
        with self.assertRaises(UserError):
            handover.action_done()
        self.assertEqual(handover.state, "draft")
        self.assertEqual(handover.open_count, 0)

    def test_03_resolve_stamps_the_resolution(self):
        handover = self._handover(name="Handover 03")
        line = self._line(handover)
        self.assertFalse(line.resolved)
        self.assertFalse(line.resolved_date)
        self.assertTrue(line.action_resolve())
        self.assertTrue(line.resolved)
        self.assertTrue(line.resolved_date)
        age = (fields.Datetime.now() - line.resolved_date).total_seconds()
        self.assertLess(abs(age), 120)
        with self.assertRaises(UserError):
            line.action_resolve()

    def test_04_open_count_ignores_resolved_items(self):
        handover = self._handover(name="Handover 04")
        first = self._line(handover, description="Pump 2 vibration")
        self._line(handover, description="Pallet 12 missing label")
        self._line(handover, description="Cold room at three degrees")
        self.assertEqual(handover.open_count, 3)
        first.action_resolve()
        handover.invalidate_recordset(["open_count"])
        self.assertEqual(handover.open_count, 2)
        self.assertEqual(len(handover.line_ids), 3)

    def test_05_reopen_refused_on_a_draft(self):
        handover = self._handover(name="Handover 05")
        with self.assertRaises(UserError):
            handover.action_reopen()
        self.assertEqual(handover.state, "draft")
        self._line(handover, description="Change the filter")
        handover.action_done()
        self.assertTrue(handover.action_reopen())
        self.assertEqual(handover.state, "draft")
        self.assertTrue(handover.action_cancel())
        self.assertEqual(handover.state, "cancelled")

    def test_06_reopening_an_item_clears_the_resolution(self):
        handover = self._handover(name="Handover 06")
        line = self._line(handover, description="Valve gasket replaced")
        line.action_resolve()
        self.assertTrue(line.resolved)
        self.assertTrue(line.action_reopen())
        self.assertFalse(line.resolved)
        self.assertFalse(line.resolved_date)
        self.assertEqual(handover.open_count, 1)
        with self.assertRaises(UserError):
            line.action_reopen()

    def test_07_item_defaults(self):
        handover = self._handover(name="Handover 07")
        line = self._line(handover, description="Default item")
        self.assertEqual(line.category, "task")
        self.assertEqual(line.severity, "medium")
        self.assertFalse(line.follow_up)
        self.assertFalse(line.resolved)
        self.assertEqual(line.sequence, 10)
        self.assertEqual(handover.shift, "morning")
        self.assertEqual(handover.date,
                         fields.Date.context_today(handover))
        self.assertEqual(len(handover.line_ids), 1)

    def test_08_company_isolation(self):
        other = self.env["res.company"].create({
            "name": "ShiftHandover Other Company"})
        handover = self._handover(name="Handover 08")
        line = self._line(handover)
        self.assertEqual(handover.company_id, self.env.company)
        self.assertNotEqual(handover.company_id, other)
        self.assertEqual(line.company_id, handover.company_id)
        foreign = self._handover(
            name="Other company handover", company_id=other.id)
        self.assertNotEqual(foreign.company_id, handover.company_id)
        mine = self.env["shift.handover"].search([
            ("company_id", "=", self.env.company.id)])
        self.assertIn(handover, mine)
        self.assertNotIn(foreign, mine)
