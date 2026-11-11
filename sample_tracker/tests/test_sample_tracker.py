# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSampleKit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "SampleKit Other Company"})
        cls.recipient = cls.env["res.partner"].create({
            "name": "SampleKit Test Partner"})
        cls.item = cls.env["sample.item"].create({
            "name": "SampleKit Test Swatch",
            "code": "SW-1",
            "category": "material",
            "followup_days": 14,
        })
        cls.demo_unit = cls.env["sample.item"].create({
            "name": "SampleKit Test Demo Unit",
            "category": "demo",
            "followup_days": 30,
        })

    def _issue(self, item=None, **values):
        defaults = {
            "item_id": (item or self.item).id,
            "recipient_id": self.recipient.id,
            "quantity": 1,
            "handed_on": date(2026, 11, 2),
        }
        defaults.update(values)
        return self.env["sample.issue"].create(defaults)

    def test_01_issue_defaults(self):
        issue = self._issue()
        self.assertEqual(issue.state, "out")
        self.assertEqual(issue.company_id, self.env.company)
        self.assertTrue(issue.name.startswith("Sample "))
        self.assertTrue(issue.follow_up_on)
        self.assertFalse(issue.converted)

    def test_02_follow_up_comes_from_the_sample(self):
        issue = self._issue(handed_on=date(2026, 11, 2))
        self.assertEqual(issue.follow_up_on, date(2026, 11, 16))
        other = self._issue(item=self.demo_unit,
                            handed_on=date(2026, 11, 2))
        self.assertEqual(other.follow_up_on, date(2026, 12, 2))

    def test_03_return_stamps_the_date(self):
        issue = self._issue()
        self.assertTrue(issue.action_return())
        self.assertEqual(issue.state, "returned")
        self.assertTrue(issue.returned_on)

    def test_04_consume_closes_the_hand_out(self):
        issue = self._issue()
        self.assertTrue(issue.action_consume())
        self.assertEqual(issue.state, "consumed")

    def test_05_double_close_is_refused(self):
        issue = self._issue()
        issue.action_return()
        with self.assertRaises(UserError):
            issue.action_return()
        with self.assertRaises(UserError):
            issue.action_consume()

    def test_06_order_placed_marks_the_sample(self):
        issue = self._issue()
        self.assertTrue(issue.action_convert())
        self.assertTrue(issue.converted)
        with self.assertRaises(UserError):
            issue.action_convert()

    def test_07_quantity_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._issue(quantity=0)
        with self.assertRaises(ValidationError):
            self._issue(quantity=-2)

    def test_08_return_before_handout_is_refused(self):
        with self.assertRaises(ValidationError):
            self._issue(handed_on=date(2026, 11, 2),
                        returned_on=date(2026, 10, 1))
        late = self._issue()
        with self.assertRaises(ValidationError):
            late.write({"returned_on": date(2026, 10, 1)})
        on_time = self._issue()
        on_time.action_return()
        self.assertEqual(on_time.state, "returned")

    def test_09_item_counters(self):
        outside = self._issue()
        closed = self._issue(quantity=2)
        closed.action_return()
        self.item.invalidate_recordset()
        self.assertEqual(self.item.issue_count, 2)
        self.assertEqual(self.item.open_issue_count, 1)
        self.assertEqual(outside.state, "out")

    def test_10_company_isolation(self):
        foreign_partner = self.env["res.partner"].sudo().create({
            "name": "SampleKit Test Foreign Partner"})
        foreign = self.env["sample.issue"].with_company(
            self.other_company).sudo().create({
            "item_id": self.item.id,
            "recipient_id": foreign_partner.id,
            "handed_on": date(2026, 11, 2),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._issue()
        self.assertEqual(local.company_id, self.env.company)
