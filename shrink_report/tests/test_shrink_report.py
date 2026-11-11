# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestShrinkWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({"name": "ShrinkWatch Other Company"})

    def _make(self, **vals):
        data = {
            "name": "SW-TEST-001",
            "product_name": "ShrinkWatch Test Widget",
            "location_name": "Aisle A",
            "reason": "damage",
            "adjustment_date": "2026-03-10",
            "quantity": 4.0,
            "unit_cost": 12.5,
        }
        data.update(vals)
        return self.env["shrink.adjustment"].create(data)

    def test_01_defaults(self):
        rec = self._make(name="SW-DEF-2026")
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.company_id, self.env.company)
        self.assertTrue(rec.active)
        self.assertFalse(rec.closed_on)

    def test_02_loss_value_compute(self):
        rec = self._make(name="SW-COMP-2026", quantity=5.0, unit_cost=10.0)
        self.assertEqual(rec.loss_value, 50.0)
        rec.write({"quantity": 2.0})
        self.assertEqual(rec.loss_value, 20.0)

    def test_03_workflow_confirm_close_reset(self):
        rec = self._make(name="SW-WF-2026", adjustment_date="2026-04-01")
        rec.action_confirm()
        self.assertEqual(rec.state, "confirmed")
        rec.action_close()
        self.assertEqual(rec.state, "closed")
        self.assertTrue(rec.closed_on)
        rec.action_reset()
        self.assertEqual(rec.state, "draft")
        self.assertFalse(rec.closed_on)

    def test_04_invalid_transitions(self):
        rec = self._make(name="SW-INV-2026", adjustment_date="2026-04-02")
        with self.assertRaises(UserError):
            rec.action_close()
        with self.assertRaises(UserError):
            rec.action_reset()
        rec.action_confirm()
        with self.assertRaises(UserError):
            rec.action_confirm()

    def test_05_quantity_constraint(self):
        with self.assertRaises(ValidationError):
            self._make(name="SW-QTY-2026", adjustment_date="2026-05-01", quantity=0.0)

    def test_06_unit_cost_constraint(self):
        with self.assertRaises(ValidationError):
            self._make(name="SW-COST-2026", adjustment_date="2026-05-02", unit_cost=-1.0)

    def test_07_search_groupby_totals(self):
        self._make(name="SW-GRP-A-2026", adjustment_date="2026-06-01", location_name="Aisle B", reason="theft", quantity=2.0, unit_cost=30.0)
        self._make(name="SW-GRP-B-2026", adjustment_date="2026-06-02", location_name="Aisle B", reason="theft", quantity=1.0, unit_cost=30.0)
        recs = self.env["shrink.adjustment"].search([("name", "in", ["SW-GRP-A-2026", "SW-GRP-B-2026"])])
        self.assertEqual(len(recs), 2)
        self.assertEqual(sum(recs.mapped("loss_value")), 90.0)

    def test_08_multi_company_isolation(self):
        own = self._make(name="SW-MC-OWN-2026", adjustment_date="2026-07-01")
        foreign = self.env["shrink.adjustment"].with_company(self.other_company).create({
            "name": "SW-MC-OTH-2026",
            "product_name": "ShrinkWatch Foreign Widget",
            "location_name": "Dock Z",
            "reason": "expiry",
            "adjustment_date": "2026-07-02",
            "quantity": 3.0,
            "unit_cost": 5.0,
            "company_id": self.other_company.id,
        })
        self.assertEqual(own.company_id, self.env.company)
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(own.company_id, foreign.company_id)
        self.assertEqual(foreign.loss_value, 15.0)

    def test_09_sequence_name_generation(self):
        rec = self.env["shrink.adjustment"].create({
            "product_name": "ShrinkWatch Seq Widget",
            "location_name": "Aisle C",
            "reason": "other",
            "adjustment_date": "2026-08-01",
            "quantity": 1.0,
            "unit_cost": 2.0,
        })
        self.assertTrue(rec.name)
        self.assertNotEqual(rec.name, "")
