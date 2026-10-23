# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRep(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pet = cls.env.ref("rep_ppwr_tracker.mat_pet")
        cls.cardboard = cls.env.ref("rep_ppwr_tracker.mat_cardboard")
        cls.product = cls.env["product.template"].create({
            "name": "Demo Biscuits", "type": "consu", "list_price": 3.5,
        })
        cls.pack = cls.env["rep.packaging"].create({
            "name": "Biscuit Box 500g", "material_id": cls.cardboard.id,
            "weight_g": 120.0, "qty_per_unit": 1.0, "level": "primary",
            "product_ids": [(6, 0, cls.product.ids)],
        })
        cls.reused = cls.env["rep.packaging"].create({
            "name": "Reusable Crate", "material_id": cls.cardboard.id,
            "weight_g": 2000.0, "qty_per_unit": 0.1, "level": "tertiary",
            "reuse": "reused",
        })

    def test_01_seed(self):
        self.assertEqual(len(self.env["rep.material"].search([])), 11)
        self.assertTrue(len(self.env["rep.tariff"].search([])) >= 10)

    def test_02_eco_cost(self):
        # 120g cardboard @148.69/t => 0.12*148.69/1000 = 0.0178
        self.assertAlmostEqual(self.pack._eco_cost_for_qty(1.0), 0.0178, places=4)
        self.assertAlmostEqual(self.pack._eco_cost_for_qty(10.0), 0.1784, places=4)

    def test_03_reuse_rules(self):
        self.pack.reuse = "reusable"
        half = self.pack._eco_cost_for_qty(1.0)
        self.assertAlmostEqual(half, 0.0089, places=4)
        self.assertEqual(self.reused._eco_cost_for_qty(100.0), 0.0)

    def test_04_alerts(self):
        self.pack.recyclability_class = "D"
        self.assertTrue(any("2030" in a for a in self.pack._ppwr_alerts()))
        self.pack.recyclability_class = "A"
        self.assertEqual(self.pack._ppwr_alerts(), [])

    def test_05_declaration(self):
        # Use a far-future year so the declaration aggregates only our own
        # ledger line. Aggregating a year that already holds real data would
        # make the totals depend on the database content.
        self.env["rep.ledger"].create({
            "packaging_id": self.pack.id, "weight_kg": 12.0,
            "amount": 1.78, "source": "delivery", "origin": "WH/OUT/1",
            "date": "2099-06-30",
        })
        decl = self.env["rep.declaration"].create({"year": 2099, "eco_org": "citeo"})
        decl.action_compute()
        self.assertEqual(len(decl.line_ids), 1)
        self.assertAlmostEqual(decl.total_tonnage, 0.012, places=3)
        self.assertAlmostEqual(decl.total_amount, 1.78)
        decl.action_close()
        self.assertEqual(decl.state, "closed")

    def test_06_deposit_rate(self):
        dep = self.env["rep.deposit"].create({
            "name": "Glass bottle 0.50", "amount": 0.5,
            "units_out": 1000, "units_back": 880,
        })
        self.assertAlmostEqual(dep.return_rate, 88.0)
