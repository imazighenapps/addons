# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDutyRoster(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "RosterBook Other Company"})
        cls.department = cls.env["hr.department"].create({
            "name": "RosterBook Duty Team"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "RosterBook Test Employee",
            "department_id": cls.department.id,
        })

    def _roster(self, **values):
        defaults = {
            "name": "RosterBook Week 2026-20",
            "date_start": "2026-05-11",
            "date_end": "2026-05-17",
        }
        defaults.update(values)
        return self.env["duty.roster"].create(defaults)

    def _slot(self, roster, **values):
        defaults = {
            "name": "RosterBook Slot A",
            "roster_id": roster.id,
            "employee_id": self.employee.id,
            "slot_start": roster.date_start,
            "slot_end": roster.date_start,
            "compensation": 100.0,
        }
        defaults.update(values)
        return self.env["duty.slot"].create(defaults)

    def test_01_roster_defaults(self):
        roster = self._roster()
        self.assertEqual(roster.state, "draft")
        self.assertEqual(roster.company_id, self.env.company)
        self.assertEqual(roster.slot_count, 0)
        self.assertEqual(roster.compensation_total, 0.0)

    def test_02_publish_requires_slot(self):
        roster = self._roster(name="RosterBook Week 2026-21")
        with self.assertRaises(ValidationError):
            roster.action_publish()

    def test_03_publish_and_close_workflow(self):
        roster = self._roster(name="RosterBook Week 2026-22")
        self._slot(roster, name="RosterBook Slot B")
        self.assertTrue(roster.action_publish())
        self.assertEqual(roster.state, "published")
        self.assertTrue(roster.action_close())
        self.assertEqual(roster.state, "closed")

    def test_04_reset_to_draft(self):
        roster = self._roster(name="RosterBook Week 2026-23")
        self._slot(roster, name="RosterBook Slot C")
        roster.action_publish()
        self.assertTrue(roster.action_reset_draft())
        self.assertEqual(roster.state, "draft")

    def test_05_counters_are_stored(self):
        roster = self._roster(name="RosterBook Week 2026-24")
        self._slot(roster, name="RosterBook Slot D1", compensation=80.0)
        self._slot(roster, name="RosterBook Slot D2", compensation=120.0)
        roster.invalidate_recordset()
        self.assertEqual(roster.slot_count, 2)
        self.assertAlmostEqual(roster.compensation_total, 200.0)

    def test_06_roster_date_constraint(self):
        with self.assertRaises(ValidationError):
            self._roster(name="RosterBook Bad Dates",
                         date_start="2026-05-20", date_end="2026-05-10")

    def test_07_slot_date_and_compensation_constraints(self):
        roster = self._roster(name="RosterBook Week 2026-25")
        with self.assertRaises(ValidationError):
            self._slot(roster, name="RosterBook Slot Bad Date",
                       slot_start="2026-05-13", slot_end="2026-05-12")
        with self.assertRaises(ValidationError):
            self._slot(roster, name="RosterBook Slot Bad Comp",
                       compensation=-10.0)

    def test_08_slot_must_be_within_roster(self):
        roster = self._roster(name="RosterBook Week 2026-26")
        with self.assertRaises(ValidationError):
            self._slot(roster, name="RosterBook Slot Outside",
                       slot_start="2026-05-18", slot_end="2026-05-18")

    def test_09_publish_closed_is_refused(self):
        roster = self._roster(name="RosterBook Week 2026-27")
        self._slot(roster, name="RosterBook Slot E")
        roster.action_publish()
        roster.action_close()
        with self.assertRaises(ValidationError):
            roster.action_publish()

    def test_10_company_isolation(self):
        foreign_department = self.env["hr.department"].with_company(
            self.other_company).create({
            "name": "RosterBook Foreign Dept",
            "company_id": self.other_company.id,
        })
        foreign_employee = self.env["hr.employee"].with_company(
            self.other_company).create({
            "name": "RosterBook Foreign Employee",
            "company_id": self.other_company.id,
            "department_id": foreign_department.id,
        })
        foreign_roster = self.env["duty.roster"].with_company(
            self.other_company).create({
            "name": "RosterBook Foreign Week",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "company_id": self.other_company.id,
        })
        foreign_slot = self.env["duty.slot"].with_company(
            self.other_company).create({
            "name": "RosterBook Foreign Slot",
            "roster_id": foreign_roster.id,
            "employee_id": foreign_employee.id,
            "slot_start": "2026-06-01",
            "slot_end": "2026-06-01",
            "compensation": 50.0,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign_roster.company_id, self.other_company)
        self.assertEqual(foreign_slot.company_id, self.other_company)
        local = self._roster(name="RosterBook Local Week")
        self.assertNotEqual(local.company_id, foreign_roster.company_id)
