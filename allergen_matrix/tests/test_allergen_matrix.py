# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAllergenDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "AllergenDesk Other Company",
        })
        cls.recipe = cls.env["allergen.recipe"].create({
            "name": "AD-RECIPE-2026-001",
            "product_name": "AllergenDesk Test Cookie",
            "line_name": "Line 1",
            "declaration_ref": "LBL-2026-001",
        })

    def _line(self, recipe=None, **values):
        defaults = {
            "recipe_id": (recipe or self.recipe).id,
            "allergen": "gluten",
            "presence": "present",
            "source": "Wheat flour",
        }
        defaults.update(values)
        return self.env["allergen.line"].create(defaults)

    def test_01_recipe_defaults(self):
        rec = self.env["allergen.recipe"].create({
            "name": "AD-RECIPE-DEF",
            "product_name": "AllergenDesk Default",
        })
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.company_id, self.env.company)
        self.assertTrue(rec.active)
        self.assertEqual(rec.allergen_count, 0)

    def test_02_validate_requires_lines(self):
        with self.assertRaises(UserError):
            self.recipe.action_validate()
        self._line()
        self.assertTrue(self.recipe.action_validate())
        self.assertEqual(self.recipe.state, "validated")

    def test_03_validate_archive_reset_workflow(self):
        self._line()
        self.recipe.action_validate()
        with self.assertRaises(UserError):
            self.recipe.action_validate()
        self.assertTrue(self.recipe.action_archive_recipe())
        self.assertEqual(self.recipe.state, "archived")
        self.assertTrue(self.recipe.action_reset())
        self.assertEqual(self.recipe.state, "draft")
        with self.assertRaises(UserError):
            self.recipe.action_reset()

    def test_04_counters_are_computed(self):
        self._line(allergen="gluten", presence="present")
        self._line(allergen="milk", presence="present")
        self._line(allergen="nuts", presence="cross")
        self.recipe.invalidate_recordset()
        self.assertEqual(self.recipe.allergen_count, 3)
        self.assertEqual(self.recipe.present_count, 2)
        self.assertEqual(self.recipe.cross_count, 1)

    def test_05_duplicate_allergen_refused(self):
        self._line(allergen="eggs")
        with self.assertRaises(Exception):
            self._line(allergen="eggs", presence="cross")

    def test_06_validated_recipe_is_locked(self):
        line = self._line(allergen="soy")
        self.recipe.action_validate()
        with self.assertRaises(UserError):
            self.recipe.write({"product_name": "Changed"})
        with self.assertRaises(UserError):
            self._line(allergen="milk")
        with self.assertRaises(UserError):
            line.write({"presence": "cross"})
        with self.assertRaises(UserError):
            line.unlink()

    def test_07_search_filters_by_counts(self):
        self._line(allergen="peanuts", presence="cross")
        self.recipe.invalidate_recordset()
        found = self.env["allergen.recipe"].search([
            ("cross_count", ">", 0),
            ("id", "=", self.recipe.id),
        ])
        self.assertIn(self.recipe, found)
        empty = self.env["allergen.recipe"].create({
            "name": "AD-RECIPE-NOCROSS",
            "product_name": "AllergenDesk No Cross",
        })
        none = self.env["allergen.recipe"].search([
            ("cross_count", ">", 0),
            ("id", "=", empty.id),
        ])
        self.assertFalse(none)

    def test_08_company_isolation(self):
        foreign = self.env["allergen.recipe"].with_company(
            self.other_company).sudo().create({
            "name": "AD-FOREIGN",
            "product_name": "AllergenDesk Foreign",
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self.env["allergen.recipe"].create({
            "name": "AD-LOCAL",
            "product_name": "AllergenDesk Local",
        })
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
