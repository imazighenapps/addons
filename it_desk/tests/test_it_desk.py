# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestITBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ITBook Other Company",
        })
        cls.asset = cls.env["it.asset"].create({
            "name": "ITBook Test Laptop",
            "serial": "ITB-SN-001",
            "model_name": "Latitude 7440",
            "asset_type": "laptop",
            "purchase_on": date(2026, 1, 10),
        })
        cls.phone = cls.env["it.asset"].create({
            "name": "ITBook Test Phone",
            "serial": "ITB-SN-002",
            "asset_type": "phone",
        })

    def _assignment(self, asset=None, **values):
        defaults = {
            "asset_id": (asset or self.asset).id,
            "holder": "ITBook Test Alice",
            "assigned_on": date(2026, 11, 10),
            "due_back_on": date(2026, 12, 10),
        }
        defaults.update(values)
        return self.env["it.assignment"].create(defaults)

    def test_01_asset_defaults(self):
        asset = self.env["it.asset"].create({
            "name": "ITBook Test Screen",
            "asset_type": "screen",
        })
        self.assertEqual(asset.state, "stock")
        self.assertEqual(asset.company_id, self.env.company)
        self.assertEqual(asset.assignment_count, 0)
        self.assertFalse(asset.current_holder)

    def test_02_assignment_sets_asset_in_use(self):
        assignment = self._assignment()
        self.assertEqual(assignment.state, "open")
        self.assertEqual(self.asset.state, "in_use")
        self.asset.invalidate_recordset()
        self.assertEqual(self.asset.current_holder, "ITBook Test Alice")
        self.assertEqual(self.asset.open_assignment_count, 1)

    def test_03_return_updates_asset(self):
        assignment = self._assignment()
        self.assertTrue(assignment.action_return())
        self.assertEqual(assignment.state, "returned")
        self.assertTrue(assignment.returned_on)
        self.asset.invalidate_recordset()
        self.assertEqual(self.asset.state, "stock")
        self.assertFalse(self.asset.current_holder)
        self.assertEqual(self.asset.open_assignment_count, 0)

    def test_04_double_return_is_refused(self):
        assignment = self._assignment()
        assignment.action_return()
        with self.assertRaises(UserError):
            assignment.action_return()

    def test_05_dates_are_validated(self):
        with self.assertRaises(ValidationError):
            self._assignment(assigned_on=date(2026, 11, 10),
                             due_back_on=date(2026, 11, 1))
        with self.assertRaises(ValidationError):
            self._assignment(assigned_on=date(2026, 11, 10),
                             returned_on=date(2026, 11, 5))

    def test_06_serial_must_be_unique_per_company(self):
        with self.assertRaises(ValidationError):
            self.env["it.asset"].create({
                "name": "ITBook Test Duplicate",
                "serial": "ITB-SN-001",
            })
        foreign = self.env["it.asset"].with_company(
            self.other_company).sudo().create({
            "name": "ITBook Test Foreign Asset",
            "serial": "ITB-SN-001",
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.serial, "ITB-SN-001")
        self.assertEqual(foreign.company_id, self.other_company)

    def test_07_asset_counters(self):
        first = self._assignment(holder="ITBook Test Alice")
        second = self._assignment(holder="ITBook Test Bob",
                                  assigned_on=date(2026, 11, 2),
                                  due_back_on=date(2026, 12, 2))
        self.assertEqual(first.state, "open")
        second.action_return()
        self.asset.invalidate_recordset()
        self.assertEqual(self.asset.assignment_count, 2)
        self.assertEqual(self.asset.open_assignment_count, 1)
        self.assertEqual(self.asset.current_holder, "ITBook Test Alice")

    def test_08_company_isolation(self):
        foreign_asset = self.env["it.asset"].with_company(
            self.other_company).sudo().create({
            "name": "ITBook Test Foreign Asset",
            "serial": "ITB-FOREIGN-1",
            "company_id": self.other_company.id,
        })
        foreign = self.env["it.assignment"].with_company(
            self.other_company).sudo().create({
            "asset_id": foreign_asset.id,
            "holder": "ITBook Test Foreign Holder",
            "assigned_on": date(2026, 12, 1),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._assignment(holder="ITBook Test Local Holder")
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)

    def test_09_assignment_name_is_computed(self):
        assignment = self._assignment(holder="ITBook Test Charlie",
                                      assigned_on=date(2027, 1, 15),
                                      due_back_on=date(2027, 2, 15))
        self.assertIn("ITBook Test Laptop", assignment.name)
        self.assertIn("ITBook Test Charlie", assignment.name)
        self.assertIn("2027-01-15", assignment.name)
