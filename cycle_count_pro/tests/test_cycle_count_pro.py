# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCycleCountPro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1)
        cls.location = cls.warehouse.lot_stock_id
        cls.product = cls.env["product.product"].create({
            "name": "Cycle Count Test Product",
            "is_storable": True,
            "standard_price": 10.0,
            "list_price": 20.0,
        })
        cls.env["stock.quant"].create({
            "product_id": cls.product.id,
            "location_id": cls.location.id,
            "quantity": 50.0,
        })

    def _plan(self, product=None):
        return self.env["cycle.count.plan"].create({
            "name": "Weekly A items",
            "warehouse_id": self.warehouse.id,
            "frequency_days": 7,
            "line_ids": [(0, 0, {
                "product_id": (product or self.product).id,
                "location_id": self.location.id,
            })],
        })

    def test_01_start_prefills_theoretical(self):
        session = self.env["cycle.count.session"].create({
            "plan_id": self._plan().id,
            "warehouse_id": self.warehouse.id,
        })
        session.action_start()
        self.assertEqual(session.state, "counting")
        self.assertEqual(len(session.line_ids), 1)
        self.assertAlmostEqual(session.line_ids.theoretical_qty, 50.0)

    def test_02_variance_is_computed(self):
        session = self.env["cycle.count.session"].create({
            "plan_id": self._plan().id,
            "warehouse_id": self.warehouse.id,
        })
        session.action_start()
        line = session.line_ids
        line.write({"counted_qty": 47.0, "is_counted": True})
        self.assertAlmostEqual(line.difference, -3.0)
        self.assertAlmostEqual(line.value_difference, -30.0)
        self.assertAlmostEqual(session.total_difference, -3.0)
        self.assertAlmostEqual(session.variance_value, -30.0)

    def test_03_validate_posts_stock_adjustment(self):
        session = self.env["cycle.count.session"].create({
            "plan_id": self._plan().id,
            "warehouse_id": self.warehouse.id,
        })
        session.action_start()
        session.line_ids.write({"counted_qty": 45.0, "is_counted": True})
        session.action_finish()
        self.assertEqual(session.state, "review")
        session.action_validate()
        self.assertEqual(session.state, "done")
        self.assertEqual(session.line_ids.state, "adjusted")
        quant = self.env["stock.quant"].search([
            ("product_id", "=", self.product.id),
            ("location_id", "=", self.location.id),
        ], limit=1)
        self.assertAlmostEqual(quant.quantity, 45.0)
        self.assertEqual(session.plan_id.state, "running")

    def test_04_finish_requires_every_line(self):
        session = self.env["cycle.count.session"].create({
            "plan_id": self._plan().id,
            "warehouse_id": self.warehouse.id,
        })
        session.action_start()
        with self.assertRaises(UserError):
            session.action_finish()

    def test_05_plan_without_product_cannot_start(self):
        plan = self.env["cycle.count.plan"].create({
            "name": "Empty plan",
            "warehouse_id": self.warehouse.id,
        })
        with self.assertRaises(UserError):
            plan.action_start()

    def test_06_cron_creates_due_sessions(self):
        plan = self._plan()
        plan.action_start()
        plan.next_date = "2020-01-01"
        self.env["cycle.count.plan"]._cron_create_sessions()
        sessions = self.env["cycle.count.session"].search([
            ("plan_id", "=", plan.id),
        ])
        self.assertTrue(sessions)
        self.assertEqual(sessions[0].state, "counting")

    def test_07_sequence_is_assigned(self):
        session = self.env["cycle.count.session"].create({
            "warehouse_id": self.warehouse.id,
        })
        self.assertNotEqual(session.name, "/")
        self.assertTrue(session.name.startswith("CYC/"))
