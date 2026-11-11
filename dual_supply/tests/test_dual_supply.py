# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDualSupply(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "DualSupply Other Company"})

    def _product(self, **values):
        defaults = {
            "name": "DualSupply Critical A",
            "critical": True,
        }
        defaults.update(values)
        return self.env["dual.product"].create(defaults)

    def _supplier(self, product, **values):
        defaults = {
            "product_id": product.id,
            "supplier_name": "DualSupply Supplier A",
            "role": "primary",
            "qualified": True,
            "lead_time_days": 5,
        }
        defaults.update(values)
        return self.env["dual.supplier"].create(defaults)

    def test_01_product_defaults(self):
        rec = self._product()
        self.assertEqual(rec.company_id, self.env.company)
        self.assertTrue(rec.critical)
        self.assertTrue(rec.active)

    def test_02_single_primary_required(self):
        prod = self._product()
        self._supplier(prod, role="primary", qualified=True)
        self._supplier(prod, supplier_name="DualSupply Supplier B",
                       role="alternate", qualified=True)
        prod.invalidate_recordset()
        self.assertEqual(prod.qualified_source_count, 2)
        self.assertFalse(prod.single_source)

    def test_03_single_source_flagged(self):
        prod = self._product(name="DualSupply Critical B")
        self._supplier(prod, role="primary", qualified=True)
        prod.invalidate_recordset()
        self.assertEqual(prod.qualified_source_count, 1)
        self.assertTrue(prod.single_source)

    def test_04_unqualified_alternate_not_counted(self):
        prod = self._product(name="DualSupply Critical C")
        self._supplier(prod, role="primary", qualified=True)
        self._supplier(prod, supplier_name="DualSupply Supplier C",
                       role="alternate", qualified=False)
        prod.invalidate_recordset()
        self.assertEqual(prod.qualified_source_count, 1)
        self.assertTrue(prod.single_source)

    def test_05_missing_primary_refused(self):
        prod = self._product(name="DualSupply Critical D")
        with self.assertRaises(ValidationError):
            self._supplier(prod, role="alternate", qualified=True)

    def test_06_multiple_primaries_refused(self):
        prod = self._product(name="DualSupply Critical E")
        self._supplier(prod, role="primary", qualified=True)
        with self.assertRaises(ValidationError):
            self._supplier(prod, supplier_name="DualSupply Supplier D",
                           role="primary", qualified=True)

    def test_07_negative_lead_time_refused(self):
        prod = self._product(name="DualSupply Critical F")
        with self.assertRaises(ValidationError):
            self._supplier(prod, role="primary", qualified=True,
                           lead_time_days=-1)

    def test_08_single_source_filter(self):
        single = self._product(name="DualSupply Critical G")
        self._supplier(single, role="primary", qualified=True)
        dual = self._product(name="DualSupply Critical H")
        self._supplier(dual, role="primary", qualified=True)
        self._supplier(dual, supplier_name="DualSupply Supplier H2",
                       role="alternate", qualified=True)
        found = self.env["dual.product"].search([
            ("single_source", "=", True)])
        self.assertIn(single, found)
        self.assertNotIn(dual, found)

    def test_09_company_isolation(self):
        foreign = self.env["dual.product"].with_company(
            self.other_company).sudo().create({
            "name": "DualSupply Foreign 2027",
            "critical": True,
            "company_id": self.other_company.id,
        })
        self.env["dual.supplier"].with_company(
            self.other_company).sudo().create({
            "product_id": foreign.id,
            "supplier_name": "DualSupply Foreign Supplier",
            "role": "primary",
            "qualified": True,
            "lead_time_days": 3,
        })
        local = self._product(name="DualSupply Local 2027")
        self._supplier(local, role="primary", qualified=True)
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
