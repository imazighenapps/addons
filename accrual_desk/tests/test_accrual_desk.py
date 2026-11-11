# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccrualDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "AccrualDesk Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "AccrualDesk Test Supplier"})
        cls.owner = cls.env.user

    def _entry(self, **values):
        defaults = {
            "name": "AccrualDesk Test Entry",
            "partner_id": self.partner.id,
            "owner_id": self.owner.id,
            "period_date": date(2026, 1, 31),
            "reverse_on": date(2026, 2, 28),
            "amount": 1200.0,
        }
        defaults.update(values)
        return self.env["accrual.entry"].create(defaults)

    def test_01_entry_defaults(self):
        entry = self._entry(name="AccrualDesk Defaults")
        self.assertEqual(entry.state, "draft")
        self.assertEqual(entry.company_id, self.env.company)
        self.assertFalse(entry.booked_on)
        self.assertFalse(entry.reversed_on)
        self.assertEqual(entry.owner_id, self.owner)

    def test_02_book_workflow(self):
        entry = self._entry(name="AccrualDesk Book")
        self.assertTrue(entry.action_book())
        self.assertEqual(entry.state, "booked")
        self.assertTrue(entry.booked_on)

    def test_03_reverse_workflow(self):
        entry = self._entry(name="AccrualDesk Reverse")
        entry.action_book()
        self.assertTrue(entry.action_reverse())
        self.assertEqual(entry.state, "reversed")
        self.assertTrue(entry.reversed_on)

    def test_04_reverse_requires_booked(self):
        entry = self._entry(name="AccrualDesk Rev Draft")
        with self.assertRaises(ValidationError):
            entry.action_reverse()

    def test_05_book_only_draft(self):
        entry = self._entry(name="AccrualDesk Book Twice")
        entry.action_book()
        with self.assertRaises(ValidationError):
            entry.action_book()

    def test_06_reset_rules(self):
        entry = self._entry(name="AccrualDesk Reset")
        entry.action_book()
        with self.assertRaises(ValidationError):
            entry.action_reset()
        entry.action_reverse()
        self.assertTrue(entry.action_reset())
        self.assertEqual(entry.state, "draft")
        self.assertFalse(entry.reversed_on)

    def test_07_amount_and_dates_constraints(self):
        with self.assertRaises(ValidationError):
            self._entry(name="AccrualDesk Zero", amount=0.0)
        with self.assertRaises(ValidationError):
            self._entry(name="AccrualDesk Neg", amount=-5.0)
        with self.assertRaises(ValidationError):
            self._entry(
                name="AccrualDesk Bad Dates",
                period_date=date(2026, 3, 31),
                reverse_on=date(2026, 3, 1),
            )

    def test_08_company_isolation(self):
        foreign = self.env["accrual.entry"].with_company(
            self.other_company).sudo().create({
            "name": "AccrualDesk Foreign",
            "partner_id": self.partner.id,
            "owner_id": self.owner.id,
            "period_date": date(2026, 1, 31),
            "reverse_on": date(2026, 2, 28),
            "amount": 500.0,
            "company_id": self.other_company.id,
        })
        local = self._entry(name="AccrualDesk Local")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
