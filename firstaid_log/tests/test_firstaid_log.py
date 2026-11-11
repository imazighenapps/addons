# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFirstAid(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "FirstAid Other Company"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "FirstAid Responsible A"})
        cls.refiller = cls.env["hr.employee"].create({
            "name": "FirstAid Refiller A"})
        cls.kit = cls.env["firstaid.kit"].create({
            "name": "FirstAid Kit Main Hall",
            "location": "FirstAid Location Hall",
            "responsible_id": cls.employee.id,
            "company_id": cls.env.company.id,
        })

    def _item(self, **values):
        defaults = {
            "name": "FirstAid Bandage",
            "kit_id": self.kit.id,
            "qty_required": 5,
            "qty_on_hand": 5,
            "expiry_date": date(2027, 6, 1),
        }
        defaults.update(values)
        return self.env["firstaid.item"].create(defaults)

    def _refill(self, **values):
        defaults = {
            "name": "FirstAid Refill A",
            "kit_id": self.kit.id,
            "refill_date": date(2026, 7, 1),
            "refilled_by_id": self.refiller.id,
        }
        defaults.update(values)
        return self.env["firstaid.refill"].create(defaults)

    def test_01_kit_defaults(self):
        self.assertEqual(self.kit.company_id, self.env.company)
        self.assertEqual(self.kit.item_count, 0)
        self.assertEqual(self.kit.missing_count, 0)
        self.assertEqual(self.kit.expired_count, 0)

    def test_02_item_defaults_and_quantities(self):
        item = self._item()
        self.assertEqual(item.qty_required, 5)
        self.assertEqual(item.qty_on_hand, 5)
        self.assertEqual(item.company_id, self.env.company)

    def test_03_required_quantity_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._item(name="FirstAid Item Zero", qty_required=0)

    def test_04_on_hand_cannot_be_negative(self):
        with self.assertRaises(ValidationError):
            self._item(name="FirstAid Item Neg", qty_on_hand=-1)

    def test_05_refill_done(self):
        refill = self._refill()
        self.assertEqual(refill.state, "draft")
        self.assertTrue(refill.action_done())
        self.assertEqual(refill.state, "done")

    def test_06_double_refill_done_is_refused(self):
        refill = self._refill(name="FirstAid Refill B")
        refill.action_done()
        with self.assertRaises(ValidationError):
            refill.action_done()

    def test_07_kit_counters_missing_and_expired(self):
        self._item(name="FirstAid Missing", qty_required=4, qty_on_hand=1)
        self._item(name="FirstAid Expired", qty_required=2, qty_on_hand=2,
                   expiry_date=date(2026, 1, 1))
        self._item(name="FirstAid Ok", qty_required=3, qty_on_hand=3,
                   expiry_date=date(2027, 12, 1))
        self.kit.invalidate_recordset()
        self.assertEqual(self.kit.item_count, 3)
        self.assertEqual(self.kit.missing_count, 1)
        self.assertEqual(self.kit.expired_count, 1)

    def test_08_refill_counter(self):
        self._refill(name="FirstAid Refill C")
        self._refill(name="FirstAid Refill D", refill_date=date(2026, 8, 1))
        self.kit.invalidate_recordset()
        self.assertEqual(self.kit.refill_count, 2)

    def test_09_items_search_by_kit(self):
        item = self._item(name="FirstAid Search Item")
        other_kit = self.env["firstaid.kit"].create({
            "name": "FirstAid Kit Workshop",
            "location": "FirstAid Location Shop",
            "responsible_id": self.employee.id,
            "company_id": self.env.company.id,
        })
        other = self.env["firstaid.item"].create({
            "name": "FirstAid Other Item",
            "kit_id": other_kit.id,
            "qty_required": 1,
            "qty_on_hand": 1,
        })
        found = self.env["firstaid.item"].search([
            ("kit_id", "=", self.kit.id)])
        self.assertIn(item, found)
        self.assertNotIn(other, found)

    def test_10_company_isolation(self):
        foreign_emp = self.env["hr.employee"].with_company(
            self.other_company).create({
            "name": "FirstAid Foreign Responsible"})
        foreign = self.env["firstaid.kit"].with_company(
            self.other_company).create({
            "name": "FirstAid Foreign Kit",
            "location": "FirstAid Foreign Location",
            "responsible_id": foreign_emp.id,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self.env["firstaid.kit"].create({
            "name": "FirstAid Local Kit",
            "location": "FirstAid Local Location",
            "responsible_id": self.employee.id,
            "company_id": self.env.company.id,
        })
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
