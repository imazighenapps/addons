# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMeterBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "MeterBook Other Company"})
        cls.meter = cls.env["meter.meter"].create({
            "name": "MeterBook Test Electricity",
            "code": "EM-01",
            "utility": "electricity",
            "location": "Main switchboard",
            "unit": "kWh",
        })
        cls.water = cls.env["meter.meter"].create({
            "name": "MeterBook Test Water",
            "utility": "water",
            "unit": "m3",
        })

    def _reading(self, meter=None, **values):
        defaults = {
            "meter_id": (meter or self.meter).id,
            "value": 100.0,
            "reading_date": date(2026, 5, 4),
        }
        defaults.update(values)
        return self.env["meter.reading"].create(defaults)

    def test_01_first_reading_sets_the_full_value(self):
        reading = self._reading()
        self.assertEqual(reading.previous_value, 0.0)
        self.assertEqual(reading.delta, 100.0)
        self.assertEqual(reading.measured_by, self.env.user)
        self.assertEqual(reading.company_id, self.env.company)

    def test_02_delta_against_the_previous_reading(self):
        first = self._reading()
        second = self._reading(value=1250.0, reading_date=date(2026, 6, 4))
        self.assertEqual(second.previous_value, first.value)
        self.assertEqual(second.delta, 1150.0)
        self.assertEqual(first.delta, 100.0)

    def test_03_one_reading_per_meter_and_day(self):
        self._reading()
        with self.assertRaises(ValidationError):
            self._reading(value=105.0)

    def test_04_same_day_on_two_meters_is_fine(self):
        self._reading()
        other = self._reading(meter=self.water)
        self.assertTrue(other.exists())
        self.assertEqual(other.delta, 100.0)

    def test_05_negative_values_are_refused(self):
        with self.assertRaises(ValidationError):
            self._reading(value=-1.0)

    def test_06_meter_follow_up_fields(self):
        self._reading()
        self._reading(value=110.0, reading_date=date(2026, 5, 5))
        self.meter.invalidate_recordset()
        self.assertEqual(self.meter.reading_count, 2)
        self.assertEqual(self.meter.last_value, 110.0)
        self.assertEqual(self.meter.last_reading_date, date(2026, 5, 5))
        self.assertEqual(self.meter.last_delta, 10.0)

    def test_07_meters_without_reading(self):
        self.water.invalidate_recordset()
        self.assertEqual(self.water.reading_count, 0)
        self.assertFalse(self.water.last_reading_date)
        self.assertEqual(self.water.last_delta, 0.0)

    def test_08_company_isolation(self):
        foreign_meter = self.env["meter.meter"].sudo().create({
            "name": "MeterBook Test Foreign",
            "company_id": self.other_company.id,
        })
        foreign = self.env["meter.reading"].sudo().create({
            "meter_id": foreign_meter.id,
            "value": 40.0,
            "reading_date": date(2026, 1, 10),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._reading(value=99.0)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)

    def test_09_change_of_order_keeps_series_consistent(self):
        self._reading(value=100.0, reading_date=date(2026, 5, 1))
        self._reading(value=200.0, reading_date=date(2026, 5, 8))
        self._reading(value=300.0, reading_date=date(2026, 5, 15))
        readings = self.env["meter.reading"].search([
            ("meter_id", "=", self.meter.id)], order="reading_date, id")
        deltas = [reading.delta for reading in readings]
        self.assertEqual(deltas, [100.0, 100.0, 100.0])
