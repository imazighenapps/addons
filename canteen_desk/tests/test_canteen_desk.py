# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCanteenBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "CanteenBook Other Company"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "CanteenBook Test Employee"})
        cls.employee_b = cls.env["hr.employee"].create({
            "name": "CanteenBook Test Employee B"})

    def _count(self, **values):
        defaults = {
            "name": "Canteen 2026-11-09-A",
            "meal_date": date(2026, 11, 9),
            "team_name": "Canteen Test Team",
            "employee_id": self.employee.id,
            "meal_count": 12,
            "cutoff_time": 10.0,
        }
        defaults.update(values)
        return self.env["canteen.count"].create(defaults)

    def test_01_count_defaults(self):
        record = self._count(name="Canteen 2026-11-09-DEF")
        self.assertEqual(record.state, "draft")
        self.assertEqual(record.company_id, self.env.company)
        self.assertFalse(record.sent_on)
        self.assertEqual(record.meal_count, 12)

    def test_02_send_stamps_date(self):
        record = self._count(name="Canteen 2026-11-10-A")
        self.assertTrue(record.action_send())
        self.assertEqual(record.state, "sent")
        self.assertTrue(record.sent_on)

    def test_03_double_send_is_refused(self):
        record = self._count(name="Canteen 2026-11-10-B")
        record.action_send()
        with self.assertRaises(UserError):
            record.action_send()

    def test_04_meal_count_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._count(name="Canteen 2026-11-10-C", meal_count=0)
        with self.assertRaises(ValidationError):
            self._count(name="Canteen 2026-11-10-D", meal_count=-3)

    def test_05_cutoff_time_range(self):
        with self.assertRaises(ValidationError):
            self._count(name="Canteen 2026-11-11-A", cutoff_time=-1.0)
        with self.assertRaises(ValidationError):
            self._count(name="Canteen 2026-11-11-B", cutoff_time=24.0)

    def test_06_responsible_employee_is_stored(self):
        record = self._count(
            name="Canteen 2026-11-11-C",
            employee_id=self.employee_b.id)
        self.assertEqual(record.employee_id, self.employee_b)

    def test_07_draft_search_finds_unsent_only(self):
        draft = self._count(name="Canteen 2026-11-12-A")
        sent = self._count(name="Canteen 2026-11-12-B", team_name="Team B")
        sent.action_send()
        found = self.env["canteen.count"].search([
            ("state", "=", "draft"),
            ("name", "in", [draft.name, sent.name])])
        self.assertIn(draft, found)
        self.assertNotIn(sent, found)

    def test_08_company_isolation(self):
        foreign_employee = self.env["hr.employee"].sudo().create({
            "name": "CanteenBook Foreign Employee"})
        foreign = self.env["canteen.count"].with_company(
            self.other_company).sudo().create({
            "name": "Canteen 2026-11-12-FOREIGN",
            "meal_date": date(2026, 11, 12),
            "team_name": "Foreign Team",
            "employee_id": foreign_employee.id,
            "meal_count": 5,
            "cutoff_time": 10.0,
            "company_id": self.other_company.id,
        })
        local = self._count(name="Canteen 2026-11-12-C")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
