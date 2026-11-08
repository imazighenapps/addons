# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCatalogSync(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env["res.partner"].create({
            "name": "Catalog Test Supplier", "supplier_rank": 1})
        cls.category = cls.env["product.category"].create({
            "name": "Catalog Test Category"})
        cls.product = cls.env["product.product"].create({
            "name": "Catalog Test Product", "type": "consu",
            "default_code": "CAT-001", "standard_price": 8.0,
            "list_price": 12.0, "categ_id": cls.category.id})
        cls.other = cls.env["product.product"].create({
            "name": "Catalog Other Product", "type": "consu",
            "default_code": "CAT-002", "standard_price": 20.0,
            "list_price": 30.0})

    def _rule(self, margin=30.0, **kwargs):
        values = {
            "name": "Catalog Margin",
            "margin_rate": margin,
        }
        values.update(kwargs)
        return self.env["catalog.margin.rule"].create(values)

    def _import(self, text, supplier=None, apply_rule=True, margin=30.0,
                **rule_kwargs):
        if apply_rule:
            self._rule(margin=margin, **rule_kwargs)
        return self.env["catalog.import"].create({
            "supplier_id": (supplier or self.supplier).id,
            "raw_text": text,
        })

    def _lines(self, batch):
        return batch.line_ids

    def test_01_simulate_matches_by_reference(self):
        batch = self._import("CAT-001;10")
        batch.action_simulate()
        self.assertEqual(len(self._lines(batch)), 1)
        line = self._lines(batch)
        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.state, "matched")
        self.assertEqual(batch.state, "simulated")
        self.assertEqual(batch.matched_count, 1)

    def test_02_unmatched_reference_is_kept(self):
        batch = self._import("NO-SUCH-REF;10")
        batch.action_simulate()
        line = self._lines(batch)
        self.assertEqual(line.state, "unmatched")
        self.assertFalse(line.product_id)
        self.assertEqual(batch.unmatched_count, 1)
        self.assertEqual(batch.matched_count, 0)

    def test_03_margin_computes_the_sale_price(self):
        batch = self._import("CAT-001;10", margin=30.0)
        batch.action_simulate()
        line = self._lines(batch)
        self.assertAlmostEqual(line.old_cost, 8.0, places=2)
        self.assertAlmostEqual(line.new_cost, 10.0, places=2)
        self.assertAlmostEqual(line.old_price, 12.0, places=2)
        self.assertAlmostEqual(line.new_price, 13.0, places=2)
        self.assertAlmostEqual(batch.cost_delta, 2.0, places=2)

    def test_04_category_rule_wins_over_the_generic_one(self):
        generic = self._rule(margin=10.0, name="Catalog Generic")
        specific = self._rule(margin=50.0, name="Catalog Specific",
                              category_id=self.category.id)
        self.assertNotEqual(generic, specific)
        batch = self._import("CAT-001;10", apply_rule=False)
        batch.action_simulate()
        self.assertAlmostEqual(batch.line_ids.new_price, 15.0, places=2)

    def test_05_apply_writes_cost_and_price(self):
        batch = self._import("CAT-001;10")
        batch.action_simulate()
        batch.action_apply()
        self.product.invalidate_recordset()
        self.assertEqual(batch.state, "applied")
        self.assertAlmostEqual(self.product.standard_price, 10.0, places=2)
        self.assertAlmostEqual(self.product.list_price, 13.0, places=2)
        self.assertEqual(batch.line_ids.state, "applied")

    def test_06_apply_requires_a_simulation(self):
        batch = self._import("CAT-001;10")
        with self.assertRaises(UserError):
            batch.action_apply()
        batch.action_simulate()
        batch.action_apply()
        with self.assertRaises(UserError):
            batch.action_apply()
        with self.assertRaises(UserError):
            batch.action_reset()

    def test_07_apply_sale_price_can_be_disabled(self):
        batch = self._import("CAT-001;10", apply_sale_price=False)
        batch.action_simulate()
        self.assertAlmostEqual(batch.line_ids.new_price, 12.0, places=2)
        batch.action_apply()
        self.product.invalidate_recordset()
        self.assertAlmostEqual(self.product.standard_price, 10.0, places=2)
        self.assertAlmostEqual(self.product.list_price, 12.0, places=2)

    def test_08_company_isolation_and_reset(self):
        other = self.env["res.company"].create({
            "name": "Catalog Other Company"})
        batch = self._import("CAT-001;10")
        batch.action_simulate()
        self.assertTrue(batch.line_ids)
        self.assertEqual(batch.company_id, self.env.company)
        self.assertNotEqual(batch.company_id, other)
        foreign = self.env["catalog.import"].create({
            "supplier_id": self.supplier.id,
            "company_id": other.id,
            "raw_text": "CAT-001;10",
        })
        self.assertNotEqual(foreign.company_id, batch.company_id)
        self.assertTrue(batch.action_reset())
        self.assertEqual(batch.state, "draft")
        self.assertFalse(batch.line_ids)
