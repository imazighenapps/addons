# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGaugeBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "GaugeBook Other Company",
        })
        cls.instrument = cls.env["calib.instrument"].create({
            "name": "GaugeBook Test Caliper",
            "serial": "GB-CAL-001",
            "location": "Bench A",
            "interval_months": 6,
            "last_calibration": date(2026, 1, 10),
        })

    def _event(self, instrument=None, **values):
        defaults = {
            "name": "GB-EVT-001",
            "instrument_id": (instrument or self.instrument).id,
            "calibration_date": date(2026, 6, 15),
            "result": "pass",
        }
        defaults.update(values)
        return self.env["calib.event"].create(defaults)

    def test_01_instrument_defaults(self):
        gauge = self.env["calib.instrument"].create({
            "name": "GaugeBook Test Micrometer",
        })
        self.assertEqual(gauge.state, "in_service")
        self.assertEqual(gauge.company_id, self.env.company)
        self.assertTrue(gauge.active)
        self.assertEqual(gauge.interval_months, 12)

    def test_02_next_due_is_computed(self):
        self.assertEqual(self.instrument.next_due, date(2026, 7, 10))
        self.instrument.write({"last_calibration": date(2026, 3, 1)})
        self.assertEqual(self.instrument.next_due, date(2026, 9, 1))

    def test_03_overdue_flag(self):
        # last calibration far in the past -> overdue
        self.instrument.write({"last_calibration": date(2025, 1, 1)})
        self.assertTrue(self.instrument.is_overdue)
        self.instrument.write({"last_calibration": date(2026, 10, 1)})
        self.assertFalse(self.instrument.is_overdue)

    def test_04_confirm_calibration_updates_instrument(self):
        event = self._event()
        self.assertEqual(event.state, "draft")
        self.assertTrue(event.action_confirm())
        self.assertEqual(event.state, "done")
        self.assertEqual(self.instrument.last_calibration, date(2026, 6, 15))
        self.assertEqual(self.instrument.next_due, date(2026, 12, 15))

    def test_05_failed_calibration_blocks_instrument(self):
        event = self._event(
            name="GB-EVT-FAIL",
            calibration_date=date(2026, 6, 20),
            result="fail",
        )
        event.action_confirm()
        self.assertEqual(self.instrument.state, "blocked")
        with self.assertRaises(UserError):
            self.instrument.action_block()
        self.assertTrue(self.instrument.action_unblock())
        self.assertEqual(self.instrument.state, "in_service")

    def test_06_interval_and_date_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["calib.instrument"].create({
                "name": "GaugeBook Bad Interval",
                "interval_months": 0,
            })
        with self.assertRaises(ValidationError):
            self._event(
                name="GB-EVT-FUTURE",
                calibration_date=date(2099, 1, 1),
            )

    def test_07_calibration_counters(self):
        self._event(name="GB-EVT-A")
        self._event(name="GB-EVT-B", calibration_date=date(2026, 7, 1))
        self.instrument.invalidate_recordset()
        self.assertEqual(self.instrument.calibration_count, 2)

    def test_08_company_isolation(self):
        foreign = self.env["calib.instrument"].with_company(
            self.other_company).sudo().create({
            "name": "GaugeBook Foreign Gauge",
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self.env["calib.instrument"].create({
            "name": "GaugeBook Local Gauge",
        })
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
