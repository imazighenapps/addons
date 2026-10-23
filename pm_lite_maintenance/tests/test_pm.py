# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env["maintenance.equipment"].create({
            "name": "Demo Compressor",
        })
        cls.hours = cls.env.ref("pm_lite_maintenance.ctype_hours")
        cls.counter = cls.env["pm.counter"].create({
            "equipment_id": cls.equipment.id,
            "type_id": cls.hours.id,
            "warning_target": 1800.0,
            "critical_target": 2000.0,
            "interval_target": 500.0,
        })
        cls.threshold = cls.env["pm.threshold"].create({
            "name": "Hours guard",
            "counter_id": cls.counter.id,
            "warn_level": 1800.0,
            "crit_level": 2000.0,
            "cooldown_hours": 0,
        })

    def test_01_seed(self):
        self.assertEqual(len(self.env["pm.counter.type"].search([])), 4)

    def test_02_reading_updates_counter(self):
        self.env["pm.reading"].create({"counter_id": self.counter.id, "value": 1500.0})
        self.assertEqual(self.counter.last_value, 1500.0)
        self.assertEqual(self.counter.next_due_value, 2000.0)
        self.assertEqual(len(self.env["pm.alert"].search(
            [("counter_id", "=", self.counter.id)])), 0)

    def test_03_warn_creates_request_once(self):
        self.env["pm.reading"].create({"counter_id": self.counter.id, "value": 1850.0})
        alerts = self.env["pm.alert"].search([("counter_id", "=", self.counter.id)])
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts.level, "warn")
        self.assertTrue(alerts.request_id)
        self.assertEqual(alerts.request_id.maintenance_type, "preventive")
        self.env["pm.reading"].create({"counter_id": self.counter.id, "value": 1860.0})
        self.assertEqual(len(self.env["pm.alert"].search(
            [("counter_id", "=", self.counter.id), ("state", "=", "open")])), 1)

    def test_04_crit_and_health(self):
        self.env["pm.reading"].create({"counter_id": self.counter.id, "value": 2100.0})
        alerts = self.env["pm.alert"].search(
            [("counter_id", "=", self.counter.id), ("level", "=", "crit")])
        self.assertTrue(alerts)
        self.assertLess(self.equipment.pm_health, 100.0)
        self.assertTrue(self.equipment.pm_health_detail)

    def test_05_negative_rejected(self):
        with self.assertRaises(ValueError):
            self.env["pm.reading"].create({"counter_id": self.counter.id, "value": -5.0})

    def test_06_ack_done(self):
        self.env["pm.reading"].create({"counter_id": self.counter.id, "value": 1850.0})
        alert = self.env["pm.alert"].search(
            [("counter_id", "=", self.counter.id)], limit=1)
        alert.action_ack()
        self.assertEqual(alert.state, "ack")
        alert.action_done()
        self.assertEqual(alert.state, "done")
