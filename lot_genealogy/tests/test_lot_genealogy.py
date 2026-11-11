# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLotGenealogy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "Genealogy Other Company"})

    def _lot(self, **values):
        defaults = {
            "name": "LG-LOT-001",
            "product_name": "Test Product",
            "produced_on": date(2026, 6, 10),
        }
        defaults.update(values)
        return self.env["lot.genealogy"].create(defaults)

    def _link(self, parent, child, **values):
        defaults = {
            "parent_lot_id": parent.id,
            "child_lot_id": child.id,
            "quantity": 1.0,
            "linked_on": date(2026, 6, 11),
        }
        defaults.update(values)
        return self.env["lot.genealogy.link"].create(defaults)

    def test_01_defaults(self):
        lot = self._lot()
        self.assertEqual(lot.company_id, self.env.company)
        self.assertFalse(lot.impacted)
        self.assertEqual(lot.parent_count, 0)
        self.assertEqual(lot.child_count, 0)

    def test_02_parent_child_counts(self):
        parent = self._lot(name="LG-P1")
        child = self._lot(name="LG-C1", produced_on=date(2026, 6, 12))
        self._link(parent, child)
        parent.invalidate_recordset(["parent_count", "child_count"])
        child.invalidate_recordset(["parent_count", "child_count"])
        self.assertEqual(parent.child_count, 1)
        self.assertEqual(child.parent_count, 1)

    def test_03_self_link_refused(self):
        lot = self._lot(name="LG-SELF")
        with self.assertRaises(ValidationError):
            self._link(lot, lot)

    def test_04_duplicate_link_refused(self):
        p = self._lot(name="LG-DP")
        c = self._lot(name="LG-DC", produced_on=date(2026, 6, 12))
        self._link(p, c)
        with self.assertRaises(ValidationError):
            self._link(p, c)

    def test_05_quantity_must_be_positive(self):
        p = self._lot(name="LG-QP")
        c = self._lot(name="LG-QC", produced_on=date(2026, 6, 12))
        with self.assertRaises(ValidationError):
            self._link(p, c, quantity=0)

    def test_06_impact_flag_actions(self):
        lot = self._lot(name="LG-IMP")
        self.assertTrue(lot.action_mark_impacted())
        self.assertTrue(lot.impacted)
        self.assertTrue(lot.action_clear_impacted())
        self.assertFalse(lot.impacted)

    def test_07_unique_name_per_company(self):
        self._lot(name="LG-UNIQ")
        with self.assertRaises(ValidationError):
            self._lot(name="LG-UNIQ", product_name="Other")

    def test_08_cross_company_link_refused(self):
        local = self._lot(name="LG-LOCAL")
        foreign = self.env["lot.genealogy"].with_company(
            self.other_company).create({
            "name": "LG-FOREIGN",
            "product_name": "Foreign",
            "produced_on": date(2026, 6, 13),
            "company_id": self.other_company.id,
        })
        with self.assertRaises(ValidationError):
            self._link(local, foreign)

    def test_09_company_isolation(self):
        foreign = self.env["lot.genealogy"].with_company(
            self.other_company).create({
            "name": "LG-ISO-F",
            "product_name": "Foreign",
            "produced_on": date(2026, 7, 1),
            "company_id": self.other_company.id,
        })
        local = self._lot(name="LG-ISO-L")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(local.company_id, foreign.company_id)
