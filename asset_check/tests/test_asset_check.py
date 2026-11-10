# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAssetCheck(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "AssetCheck Other Company"})
        cls.inventory = cls.env["asset.inventory"].create({
            "name": "Asset Check 2026-Q4",
            "planned_date": date(2026, 11, 20),
        })

    def _line(self, inventory=None, **values):
        defaults = {
            "inventory_id": (inventory or self.inventory).id,
            "asset_tag": "AST-2026-001",
            "asset_name": "AssetCheck Test Laptop",
            "expected_location": "Office A",
        }
        defaults.update(values)
        return self.env["asset.inventory.line"].create(defaults)

    def test_01_defaults(self):
        self.assertEqual(self.inventory.state, "draft")
        self.assertEqual(self.inventory.company_id, self.env.company)
        self.assertEqual(self.inventory.line_count, 0)
        self.assertFalse(self.inventory.closed_on)

    def test_02_line_results_update_totals(self):
        self._line(result="found", checked_on=date(2026, 11, 20))
        self._line(asset_tag="AST-2026-002", asset_name="AssetCheck Printer",
                   result="missing")
        self._line(asset_tag="AST-2026-003", asset_name="AssetCheck Screen",
                   result="moved", observed_location="Office B")
        self.inventory.invalidate_recordset()
        self.assertEqual(self.inventory.line_count, 3)
        self.assertEqual(self.inventory.found_count, 1)
        self.assertEqual(self.inventory.missing_count, 1)
        self.assertEqual(self.inventory.moved_count, 1)

    def test_03_start_close_workflow(self):
        self._line(result="found")
        self.assertTrue(self.inventory.action_start())
        self.assertEqual(self.inventory.state, "in_progress")
        self.assertTrue(self.inventory.action_close())
        self.assertEqual(self.inventory.state, "closed")
        self.assertTrue(self.inventory.closed_on)

    def test_04_reset_and_invalid_transitions(self):
        self._line(result="found")
        with self.assertRaises(UserError):
            self.inventory.action_close()
        self.inventory.action_start()
        self.assertTrue(self.inventory.action_reset())
        self.assertEqual(self.inventory.state, "draft")
        with self.assertRaises(UserError):
            self.inventory.action_reset()

    def test_05_close_requires_all_results(self):
        self._line()
        self.inventory.action_start()
        with self.assertRaises(UserError):
            self.inventory.action_close()
        self.inventory.line_ids.write({"result": "found"})
        self.inventory.action_close()
        self.assertEqual(self.inventory.state, "closed")

    def test_06_closed_campaign_is_locked(self):
        self._line(result="found")
        self.inventory.action_start()
        self.inventory.action_close()
        with self.assertRaises(UserError):
            self.inventory.write({"name": "Asset Check Changed"})
        with self.assertRaises(UserError):
            self._line(asset_tag="AST-2026-099", asset_name="Late Asset")

    def test_07_moved_requires_observed_location(self):
        with self.assertRaises(ValidationError):
            self._line(result="moved")
        line = self._line(asset_tag="AST-2026-010", result="moved",
                          observed_location="Warehouse 2")
        self.assertEqual(line.observed_location, "Warehouse 2")

    def test_08_company_isolation(self):
        foreign = self.env["asset.inventory"].with_company(
            self.other_company).create({
            "name": "Asset Check Foreign 2026",
            "planned_date": date(2026, 12, 5),
            "responsible_id": self.env.user.id,
            "company_id": self.other_company.id,
        })
        self.env["asset.inventory.line"].with_company(
            self.other_company).create({
            "inventory_id": foreign.id,
            "asset_tag": "AST-F-001",
            "asset_name": "Foreign Asset",
            "result": "found",
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(self.inventory.company_id, self.env.company)
        self.assertEqual(foreign.line_count, 1)
        self.assertEqual(foreign.found_count, 1)
