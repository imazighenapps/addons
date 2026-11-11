# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestShelfLife(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ShelfLife Other Company"})

    def _lot(self, **values):
        defaults = {
            "name": "LOT-SL-2026-001",
            "product_name": "ShelfLife Yogurt 2026",
            "location_name": "Cold Room A",
            "quantity": 12.0,
            "received_date": date(2026, 1, 5),
            "expiry_date": date(2026, 1, 20),
            "warning_days": 7,
        }
        defaults.update(values)
        return self.env["shelf.lot"].create(defaults)

    def test_01_defaults_and_days_left(self):
        lot = self._lot()
        self.assertEqual(lot.state, "fresh")
        self.assertEqual(lot.company_id, self.env.company)
        self.assertIsInstance(lot.days_left, int)

    def test_02_refresh_status_expiring_and_expired(self):
        today = fields_date = date.today()
        expiring = self._lot(name="LOT-SL-EXPIRING", product_name="Milk 2026",
                             expiry_date=today + timedelta(days=3),
                             received_date=today - timedelta(days=2))
        expiring.action_refresh_status()
        self.assertEqual(expiring.state, "expiring")
        expired = self._lot(name="LOT-SL-EXPIRED", product_name="Cheese 2026",
                            expiry_date=today - timedelta(days=1),
                            received_date=today - timedelta(days=10))
        expired.action_refresh_status()
        self.assertEqual(expired.state, "expired")

    def test_03_quarantine_consume_dispose(self):
        lot = self._lot(name="LOT-SL-Q-2026")
        lot.action_refresh_status()
        self.assertTrue(lot.action_quarantine())
        self.assertEqual(lot.state, "quarantined")
        lot2 = self._lot(name="LOT-SL-C-2026", expiry_date=date(2026, 12, 31),
                         received_date=date(2026, 12, 1))
        self.assertTrue(lot2.action_consume())
        self.assertEqual(lot2.state, "consumed")
        lot3 = self._lot(name="LOT-SL-D-2026", expiry_date=date(2026, 12, 30),
                         received_date=date(2026, 12, 1))
        self.assertTrue(lot3.action_dispose())
        self.assertEqual(lot3.state, "disposed")

    def test_04_expired_lot_cannot_be_consumed(self):
        today = date.today()
        lot = self._lot(name="LOT-SL-NOCONSUME", expiry_date=today - timedelta(days=2),
                        received_date=today - timedelta(days=20))
        lot.action_refresh_status()
        self.assertEqual(lot.state, "expired")
        with self.assertRaises(UserError):
            lot.action_consume()

    def test_05_date_and_value_constraints(self):
        with self.assertRaises(ValidationError):
            self._lot(name="LOT-SL-BADDATE",
                      received_date=date(2026, 5, 10),
                      expiry_date=date(2026, 5, 1))
        with self.assertRaises(ValidationError):
            self._lot(name="LOT-SL-BADQTY", quantity=0.0)
        with self.assertRaises(ValidationError):
            self._lot(name="LOT-SL-BADWARN", warning_days=-1)

    def test_06_closed_lot_actions_refused(self):
        lot = self._lot(name="LOT-SL-CLOSED", expiry_date=date(2026, 12, 31),
                        received_date=date(2026, 12, 1))
        lot.action_consume()
        with self.assertRaises(UserError):
            lot.action_dispose()
        lot2 = self._lot(name="LOT-SL-DISC", expiry_date=date(2026, 12, 31),
                         received_date=date(2026, 12, 2))
        lot2.action_dispose()
        with self.assertRaises(UserError):
            lot2.action_quarantine()

    def test_07_alert_flag(self):
        today = date.today()
        lot = self._lot(name="LOT-SL-ALERT", expiry_date=today + timedelta(days=2),
                        received_date=today - timedelta(days=1), warning_days=5)
        lot.action_refresh_status()
        self.assertTrue(lot.is_alert)
        self.assertEqual(lot.state, "expiring")

    def test_08_refresh_skips_closed_states(self):
        lot = self._lot(name="LOT-SL-SKIP", expiry_date=date(2026, 12, 31),
                        received_date=date(2026, 12, 1))
        lot.action_quarantine()
        self.assertTrue(lot.action_refresh_status())
        self.assertEqual(lot.state, "quarantined")

    def test_09_company_isolation(self):
        foreign = self.env["shelf.lot"].with_company(
            self.other_company).sudo().create({
            "name": "FOREIGN-LOT-2026",
            "product_name": "Foreign Product",
            "location_name": "Foreign Room",
            "quantity": 5.0,
            "received_date": date(2026, 6, 1),
            "expiry_date": date(2026, 6, 20),
            "warning_days": 5,
            "company_id": self.other_company.id,
        })
        local = self._lot(name="LOT-SL-LOCAL-2026")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
