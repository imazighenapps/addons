# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDowntime(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "Downtime Other Company"})
        cls.machine = cls.env["downtime.machine"].create({
            "name": "Downtime Press A",
            "code": "PRS-A",
            "planned_minutes": 480,
        })
        cls.machine_b = cls.env["downtime.machine"].create({
            "name": "Downtime Press B",
            "code": "PRS-B",
            "planned_minutes": 240,
        })

    def _event(self, machine=None, **values):
        defaults = {
            "name": "Downtime Event A",
            "machine_id": (machine or self.machine).id,
            "reason": "Power loss",
            "start_at": datetime(2026, 11, 10, 8, 0, 0),
            "end_at": datetime(2026, 11, 10, 9, 0, 0),
            "state": "closed",
        }
        defaults.update(values)
        return self.env["downtime.event"].create(defaults)

    def test_01_machine_defaults(self):
        machine = self.machine
        self.assertEqual(machine.company_id, self.env.company)
        self.assertEqual(machine.stop_count, 0)
        self.assertEqual(machine.downtime_minutes, 0.0)
        self.assertEqual(machine.availability_rate, 100.0)

    def test_02_event_duration_computed(self):
        event = self._event(name="Downtime Event Duration")
        self.assertEqual(event.duration_minutes, 60.0)
        self.assertEqual(event.state, "closed")

    def test_03_machine_metrics(self):
        self._event(name="Downtime Event M1",
                    start_at=datetime(2026, 11, 10, 8, 0, 0),
                    end_at=datetime(2026, 11, 10, 9, 0, 0))
        self._event(name="Downtime Event M2",
                    start_at=datetime(2026, 11, 10, 10, 0, 0),
                    end_at=datetime(2026, 11, 10, 10, 30, 0))
        self.machine.invalidate_recordset()
        self.assertEqual(self.machine.stop_count, 2)
        self.assertEqual(self.machine.open_stop_count, 0)
        self.assertEqual(self.machine.downtime_minutes, 90.0)
        self.assertEqual(self.machine.mttr_minutes, 45.0)
        self.assertAlmostEqual(self.machine.availability_rate, 81.25, places=2)

    def test_04_open_stop_and_close_action(self):
        event = self._event(name="Downtime Running",
                            end_at=False, state="open")
        self.machine.invalidate_recordset()
        self.assertEqual(self.machine.open_stop_count, 1)
        event.write({"end_at": datetime(2026, 11, 10, 8, 20, 0)})
        self.assertTrue(event.action_close_stop())
        self.assertEqual(event.state, "closed")
        self.assertEqual(event.duration_minutes, 20.0)

    def test_05_double_close_is_refused(self):
        event = self._event(name="Downtime Closed")
        with self.assertRaises(ValidationError):
            event.action_close_stop()

    def test_06_end_before_start_is_refused(self):
        with self.assertRaises(ValidationError):
            self._event(
                name="Downtime Bad Dates",
                start_at=datetime(2026, 11, 10, 9, 0, 0),
                end_at=datetime(2026, 11, 10, 8, 0, 0))

    def test_07_planned_minutes_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.env["downtime.machine"].create({
                "name": "Downtime Invalid Machine",
                "planned_minutes": 0,
            })

    def test_08_company_isolation(self):
        foreign_machine = self.env["downtime.machine"].with_company(
            self.other_company).sudo().create({
                "name": "Downtime Foreign Machine",
                "planned_minutes": 300,
                "company_id": self.other_company.id,
            })
        foreign_event = self.env["downtime.event"].with_company(
            self.other_company).sudo().create({
                "name": "Downtime Foreign Event",
                "machine_id": foreign_machine.id,
                "reason": "Foreign stop",
                "start_at": datetime(2026, 11, 11, 8, 0, 0),
                "end_at": datetime(2026, 11, 11, 8, 15, 0),
                "state": "closed",
                "company_id": self.other_company.id,
            })
        self.assertEqual(foreign_machine.company_id, self.other_company)
        self.assertEqual(foreign_event.company_id, self.other_company)
        local_event = self._event(name="Downtime Local Event",
                                  machine=self.machine_b)
        self.assertNotEqual(local_event.company_id, foreign_event.company_id)

    def test_09_filter_running_and_closed_events(self):
        running = self._event(name="Downtime Running Filter",
                              machine=self.machine_b,
                              end_at=False, state="open")
        closed = self._event(name="Downtime Closed Filter")
        found_running = self.env["downtime.event"].search([
            ("state", "=", "open")])
        found_closed = self.env["downtime.event"].search([
            ("state", "=", "closed")])
        self.assertIn(running, found_running)
        self.assertIn(closed, found_closed)
        self.assertNotIn(closed, found_running)
