# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestColdChain(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ColdChain Other Company"})
        cls.point = cls.env["cold.point"].create({
            "name": "ColdChain Test Freezer",
            "ref": "FR1",
            "location": "Building A - Cold room 1",
            "min_temp": -22.0,
            "max_temp": -16.0,
        })
        cls.warehouse_point = cls.env["cold.point"].create({
            "name": "ColdChain Test Warehouse",
            "location": "Building B",
            "min_temp": -1.0,
            "max_temp": 4.0,
        })

    def _reading(self, **values):
        defaults = {
            "point_id": self.point.id,
            "temperature": -18.0,
            "recorded_at": datetime(2026, 5, 4, 9, 0),
        }
        defaults.update(values)
        return self.env["cold.reading"].create(defaults)

    def test_01_reading_in_range(self):
        reading = self._reading()
        self.assertEqual(reading.status, "ok")
        self.assertFalse(reading.corrected)
        self.assertEqual(reading.measured_by, self.env.user)
        self.assertEqual(reading.company_id, self.env.company)

    def test_02_breach_on_both_sides_of_the_range(self):
        too_warm = self._reading(temperature=-14.0)
        self.assertEqual(too_warm.status, "breach")
        too_cold = self._reading(temperature=-25.0)
        self.assertEqual(too_cold.status, "breach")
        edge = self._reading(temperature=-22.0)
        self.assertEqual(edge.status, "ok")

    def test_03_correction_needs_a_note(self):
        reading = self._reading(temperature=-14.0)
        with self.assertRaises(UserError):
            reading.action_correct()
        reading.correction_note = "Compressor cleaned, back in range."
        self.assertTrue(reading.action_correct())
        self.assertTrue(reading.corrected)
        self.assertTrue(reading.corrected_at)

    def test_04_in_range_reading_cannot_be_corrected(self):
        reading = self._reading()
        with self.assertRaises(UserError):
            reading.action_correct()

    def test_05_reopen_clears_the_correction(self):
        reading = self._reading(temperature=-14.0,
                                correction_note="Door was left open.")
        reading.action_correct()
        self.assertTrue(reading.corrected)
        self.assertTrue(reading.action_reopen())
        self.assertFalse(reading.corrected)
        self.assertFalse(reading.corrected_at)

    def test_06_point_range_is_checked(self):
        with self.assertRaises(ValidationError):
            self.env["cold.point"].create({
                "name": "ColdChain Test Reversed",
                "min_temp": 0.0,
                "max_temp": -5.0,
            })
        with self.assertRaises(ValidationError):
            self.warehouse_point.write({"max_temp": -2.0})

    def test_07_point_counters(self):
        self._reading()
        first_breach = self._reading(temperature=-14.5)
        self.point.invalidate_recordset()
        self.assertEqual(self.point.reading_count, 2)
        self.assertEqual(self.point.open_breach_count, 1)
        first_breach.correction_note = "Compressor cleaned."
        first_breach.action_correct()
        self._reading(temperature=-14.2, correction_note="Door shut."). \
            action_correct()
        self.point.invalidate_recordset()
        self.assertEqual(self.point.reading_count, 3)
        self.assertEqual(self.point.open_breach_count, 0)

    def test_08_company_isolation(self):
        foreign_point = self.env["cold.point"].sudo().create({
            "name": "ColdChain Test Foreign",
            "min_temp": -20.0,
            "max_temp": -10.0,
            "company_id": self.other_company.id,
        })
        foreign = self.env["cold.reading"].sudo().create({
            "point_id": foreign_point.id,
            "temperature": -15.0,
            "recorded_at": datetime(2000, 1, 1, 9, 0),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        breaches = self.env["cold.reading"].search([
            ("point_id", "=", self.point.id), ("status", "=", "breach")])
        for breach in breaches:
            self.assertEqual(breach.company_id, self.env.company)
