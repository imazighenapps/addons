# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSDSWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "SDSWatch Other Company",
        })
        cls.product = cls.env["sds.product"].create({
            "name": "SDSWatch Test Solvent",
            "supplier": "SDSWatch Test Supplier",
            "hazard_class": "flammable",
            "current_issue": date(2026, 1, 5),
            "current_expiry": date(2027, 1, 5),
        })

    def _version(self, product=None, **values):
        defaults = {
            "name": "SDS-REV-1",
            "product_id": (product or self.product).id,
            "issue_date": date(2026, 1, 5),
            "expiry_date": date(2027, 1, 5),
        }
        defaults.update(values)
        return self.env["sds.version"].create(defaults)

    def test_01_product_defaults(self):
        chem = self.env["sds.product"].create({
            "name": "SDSWatch Test Acid",
            "hazard_class": "corrosive",
        })
        self.assertEqual(chem.company_id, self.env.company)
        self.assertTrue(chem.active)
        self.assertTrue(chem.is_missing)
        self.assertFalse(chem.is_lapsed)

    def test_02_lapsed_flag(self):
        self.assertFalse(self.product.is_lapsed)
        self.product.write({
            "current_issue": date(2025, 12, 1),
            "current_expiry": date(2026, 1, 1),
        })
        self.assertTrue(self.product.is_lapsed)
        self.product.write({
            "current_issue": date(2027, 1, 1),
            "current_expiry": date(2027, 12, 31),
        })
        self.assertFalse(self.product.is_lapsed)

    def test_03_missing_sheet_flag(self):
        chem = self.env["sds.product"].create({
            "name": "SDSWatch Test Empty",
            "hazard_class": "other",
        })
        self.assertTrue(chem.is_missing)
        chem.write({
            "current_issue": date(2026, 3, 1),
            "current_expiry": date(2027, 3, 1),
        })
        self.assertFalse(chem.is_missing)

    def test_04_date_constraints_on_product(self):
        with self.assertRaises(ValidationError):
            self.env["sds.product"].create({
                "name": "SDSWatch Bad Dates",
                "current_issue": date(2027, 1, 1),
                "current_expiry": date(2026, 1, 1),
            })

    def test_05_date_constraints_on_version(self):
        with self.assertRaises(ValidationError):
            self._version(
                name="SDS-BAD",
                issue_date=date(2027, 6, 1),
                expiry_date=date(2027, 1, 1),
            )

    def test_06_mark_version_current_updates_product(self):
        v1 = self._version(name="SDS-REV-A")
        v2 = self._version(
            name="SDS-REV-B",
            issue_date=date(2026, 8, 1),
            expiry_date=date(2027, 8, 1),
        )
        self.assertTrue(v2.action_mark_current())
        self.assertTrue(v2.is_current)
        self.assertFalse(v1.is_current)
        self.assertEqual(self.product.current_issue, date(2026, 8, 1))
        self.assertEqual(self.product.current_expiry, date(2027, 8, 1))
        self.assertTrue(v1.action_mark_current())
        self.assertTrue(v1.is_current)
        self.assertFalse(v2.is_current)

    def test_07_version_counter(self):
        self._version(name="SDS-CNT-1")
        self._version(
            name="SDS-CNT-2",
            issue_date=date(2026, 5, 1),
            expiry_date=date(2027, 5, 1),
        )
        self.product.invalidate_recordset()
        self.assertEqual(self.product.version_count, 2)

    def test_08_company_isolation(self):
        foreign = self.env["sds.product"].with_company(
            self.other_company).sudo().create({
            "name": "SDSWatch Foreign Chemical",
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self.env["sds.product"].create({
            "name": "SDSWatch Local Chemical",
        })
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
