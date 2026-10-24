# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWarrantyTrack(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Warranty Customer", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "Warranty Machine", "type": "consu",
            "is_storable": True, "list_price": 1000.0})

    def _warranty(self, start=None, months=12):
        return self.env["warranty.registration"].create({
            "partner_id": self.partner.id,
            "product_id": self.product.id,
            "serial_number": "SN-0001",
            "date_start": start or date(2026, 1, 1),
            "duration_months": months,
        })

    def _claim(self, warranty, **kwargs):
        vals = {
            "registration_id": warranty.id,
            "issue": "Motor does not start",
            "cost": 100.0,
            "vendor_recovery": 40.0,
        }
        vals.update(kwargs)
        return self.env["warranty.claim"].create(vals)

    def test_01_registration(self):
        warranty = self._warranty()
        self.assertTrue(warranty.name.startswith("WAR/"))
        self.assertEqual(warranty.date_end, date(2027, 1, 1))
        self.assertTrue(warranty.is_covered)

    def test_02_claim_coverage(self):
        warranty = self._warranty()
        claim = self._claim(warranty)
        self.assertTrue(claim.covered)
        claim.action_approve()
        self.assertEqual(claim.state, "approved")
        claim.action_done()
        self.assertEqual(claim.state, "done")
        self.assertEqual(warranty.claim_count, 1)
        self.assertAlmostEqual(warranty.total_claim_cost, 100.0, places=2)

    def test_03_expired_warranty_blocks(self):
        warranty = self._warranty(start=date(2020, 1, 1), months=12)
        warranty.action_expire()
        self.assertEqual(warranty.state, "expired")
        claim = self._claim(warranty)
        self.assertFalse(claim.covered)
        with self.assertRaises(UserError):
            claim.action_approve()

    def test_04_goodwill_allows(self):
        warranty = self._warranty(start=date(2020, 1, 1), months=12)
        warranty.action_expire()
        claim = self._claim(warranty, goodwill=True)
        claim.action_approve()
        self.assertEqual(claim.state, "approved")

    def test_05_recovery_cannot_exceed_cost(self):
        warranty = self._warranty()
        with self.assertRaises(Exception):
            self._claim(warranty, cost=50.0, vendor_recovery=80.0)

    def test_06_cron_expire(self):
        warranty = self._warranty(start=date(2020, 1, 1), months=1)
        self.env["warranty.registration"]._cron_expire()
        self.assertEqual(warranty.state, "expired")

    def test_07_void(self):
        warranty = self._warranty()
        warranty.action_void()
        self.assertEqual(warranty.state, "void")
        self.assertFalse(warranty.is_covered)
