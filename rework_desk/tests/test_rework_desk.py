# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRework(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "Rework Other Company"})
        cls.user = cls.env.user

    def _reject(self, **values):
        defaults = {
            "name": "REJ-2026-001",
            "product_ref": "Valve X",
            "quantity": 10.0,
            "reason": "Rework Test Surface defect",
            "detected_on": date(2026, 5, 2),
        }
        defaults.update(values)
        return self.env["rwk.reject"].create(defaults)

    def _order(self, reject, **values):
        defaults = {
            "name": "RWK-2026-001",
            "reject_id": reject.id,
            "quantity": 5.0,
            "planned_on": date(2026, 5, 3),
            "owner_id": self.user.id,
        }
        defaults.update(values)
        return self.env["rwk.order"].create(defaults)

    def test_01_defaults(self):
        rej = self._reject()
        self.assertEqual(rej.state, "open")
        self.assertEqual(rej.company_id, self.env.company)
        self.assertEqual(rej.order_count, 0)

    def test_02_order_workflow(self):
        rej = self._reject(name="REJ-2026-002")
        order = self._order(rej, name="RWK-2026-002")
        self.assertEqual(order.state, "draft")
        self.assertTrue(order.action_plan())
        self.assertEqual(rej.state, "in_rework")
        self.assertTrue(order.action_start())
        self.assertTrue(order.action_done())
        self.assertEqual(order.state, "done")
        self.assertTrue(order.done_on)

    def test_03_reject_close_requires_done_order(self):
        rej = self._reject(name="REJ-2026-003")
        with self.assertRaises(ValidationError):
            rej.action_close()

    def test_04_quantity_constraints(self):
        with self.assertRaises(ValidationError):
            self._reject(name="REJ-2026-004", quantity=0)
        rej = self._reject(name="REJ-2026-005", quantity=4)
        with self.assertRaises(ValidationError):
            self._order(rej, name="RWK-2026-005", quantity=5)

    def test_05_invalid_transitions(self):
        rej = self._reject(name="REJ-2026-006")
        order = self._order(rej, name="RWK-2026-006")
        with self.assertRaises(ValidationError):
            order.action_start()
        with self.assertRaises(ValidationError):
            order.action_done()

    def test_06_counters(self):
        rej = self._reject(name="REJ-2026-007", quantity=12)
        o1 = self._order(rej, name="RWK-2026-007A", quantity=4)
        o2 = self._order(rej, name="RWK-2026-007B", quantity=3)
        o1.action_plan()
        o1.action_start()
        o1.action_done()
        rej.invalidate_recordset()
        self.assertEqual(rej.order_count, 2)
        self.assertEqual(rej.done_order_count, 1)
        self.assertEqual(rej.reworked_qty, 4)
        self.assertEqual(o2.state, "draft")

    def test_07_done_before_plan_refused(self):
        rej = self._reject(name="REJ-2026-008")
        with self.assertRaises(ValidationError):
            self._order(rej, name="RWK-2026-008", planned_on=date(2026, 5, 5),
                        done_on=date(2026, 5, 4))

    def test_08_company_isolation(self):
        rej = self._reject(name="REJ-2026-009")
        foreign = self.env["rwk.reject"].with_company(
            self.other_company).sudo().create({
            "name": "REJ-FOREIGN-2026",
            "product_ref": "Foreign",
            "quantity": 2,
            "reason": "Other",
            "detected_on": date(2026, 6, 1),
            "company_id": self.other_company.id,
        })
        self.assertEqual(rej.company_id, self.env.company)
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(rej.company_id, foreign.company_id)
