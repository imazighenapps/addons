# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCylinderDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "CylinderDesk Other Company"})
        cls.supplier = cls.env["res.partner"].create({
            "name": "CylinderDesk Test Supplier"})
        cls.cylinder = cls.env["cylinder.type"].create({
            "name": "CylinderDesk Test Oxygen",
            "gas": "Oxygen",
            "capacity_liters": 50.0,
            "rental_rate": 12.5,
        })

    def _custody(self, cylinder=None, **values):
        defaults = {
            "cylinder_type_id": (cylinder or self.cylinder).id,
            "supplier_id": self.supplier.id,
            "received_qty": 4,
            "received_on": date(2026, 11, 9),
        }
        defaults.update(values)
        return self.env["cylinder.custody"].create(defaults)

    def test_01_custody_defaults(self):
        line = self._custody()
        self.assertEqual(line.state, "open")
        self.assertEqual(line.company_id, self.env.company)
        self.assertTrue(line.name.startswith("Custody "))
        self.assertEqual(line.on_site_qty, 4)
        self.assertEqual(line.returned_qty, 0)

    def test_02_on_site_balance_is_computed(self):
        line = self._custody(received_qty=6)
        self.assertEqual(line.on_site_qty, 6)
        line.write({"returned_qty": 2})
        self.assertEqual(line.on_site_qty, 4)

    def test_03_return_all_closes_the_line(self):
        line = self._custody(received_qty=3)
        self.assertTrue(line.action_return())
        self.assertEqual(line.state, "closed")
        self.assertEqual(line.returned_qty, 3)
        self.assertTrue(line.returned_on)
        self.assertEqual(line.on_site_qty, 0)

    def test_04_double_return_is_refused(self):
        line = self._custody()
        line.action_return()
        with self.assertRaises(ValidationError):
            line.action_return()

    def test_05_received_quantity_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._custody(received_qty=0)
        with self.assertRaises(ValidationError):
            self._custody(received_qty=-2)

    def test_06_returned_quantity_cannot_exceed_received(self):
        with self.assertRaises(ValidationError):
            self._custody(received_qty=2, returned_qty=3)
        with self.assertRaises(ValidationError):
            self._custody(returned_qty=-1)

    def test_07_return_before_received_is_refused(self):
        with self.assertRaises(ValidationError):
            self._custody(received_on=date(2026, 11, 9),
                          returned_on=date(2026, 11, 2))

    def test_08_type_counters(self):
        open_line = self._custody(received_qty=2)
        closed = self._custody(received_qty=1)
        closed.action_return()
        self.cylinder.invalidate_recordset()
        self.assertEqual(self.cylinder.custody_count, 2)
        self.assertEqual(self.cylinder.open_custody_count, 1)
        self.assertTrue(open_line)

    def test_09_company_isolation(self):
        foreign_supplier = self.env["res.partner"].sudo().create({
            "name": "CylinderDesk Test Foreign Supplier"})
        foreign = self.env["cylinder.custody"].with_company(
            self.other_company).sudo().create({
            "cylinder_type_id": self.cylinder.id,
            "supplier_id": foreign_supplier.id,
            "received_qty": 1,
            "received_on": date(2026, 11, 9),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._custody()
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
