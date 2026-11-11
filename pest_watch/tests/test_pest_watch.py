# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPestWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "PestWatch Other Company",
        })
        cls.station = cls.env["pest.station"].create({
            "name": "PestWatch Test Station",
            "code": "PW-ST-001",
            "location": "Warehouse North",
            "station_type": "bait",
            "interval_days": 30,
            "last_check": date(2026, 10, 1),
        })

    def _inspection(self, station=None, **values):
        defaults = {
            "name": "PW-INSP-001",
            "station_id": (station or self.station).id,
            "inspection_date": date(2026, 10, 20),
            "contractor": "PestWatch Test Contractor",
            "result": "clear",
        }
        defaults.update(values)
        return self.env["pest.inspection"].create(defaults)

    def test_01_station_defaults(self):
        st = self.env["pest.station"].create({
            "name": "PestWatch Default Station",
            "code": "PW-ST-DEF",
            "location": "Dock",
        })
        self.assertEqual(st.state, "active")
        self.assertEqual(st.company_id, self.env.company)
        self.assertTrue(st.active)
        self.assertEqual(st.interval_days, 30)

    def test_02_next_check_is_computed(self):
        self.assertEqual(self.station.next_check, date(2026, 10, 31))
        self.station.write({"last_check": date(2026, 11, 1)})
        self.assertEqual(self.station.next_check, date(2026, 12, 1))

    def test_03_overdue_flag(self):
        self.station.write({"last_check": date(2025, 1, 1)})
        self.assertTrue(self.station.is_overdue)
        self.station.write({"last_check": date(2026, 11, 5)})
        self.assertFalse(self.station.is_overdue)

    def test_04_confirm_inspection_updates_station(self):
        insp = self._inspection(inspection_date=date(2026, 10, 25))
        self.assertTrue(insp.action_confirm())
        self.assertEqual(insp.state, "done")
        self.assertEqual(self.station.last_check, date(2026, 10, 25))
        self.assertEqual(self.station.next_check, date(2026, 11, 24))

    def test_05_finding_lifecycle(self):
        insp = self._inspection(
            name="PW-INSP-FIND",
            inspection_date=date(2026, 10, 26),
            result="activity",
        )
        insp.action_confirm()
        self.assertEqual(insp.finding_state, "open")
        self.assertTrue(insp.action_close_finding())
        self.assertEqual(insp.finding_state, "closed")
        with self.assertRaises(UserError):
            insp.action_close_finding()

    def test_06_interval_and_date_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["pest.station"].create({
                "name": "PestWatch Bad Interval",
                "code": "PW-BAD-INT",
                "location": "Lab",
                "interval_days": 0,
            })
        with self.assertRaises(ValidationError):
            self._inspection(
                name="PW-INSP-FUTURE",
                inspection_date=date(2099, 1, 1),
            )
        with self.assertRaises(ValidationError):
            self._inspection(
                name="PW-INSP-CLEAROPEN",
                result="clear",
                finding_state="open",
            )

    def test_07_inspection_counters_and_filters(self):
        self._inspection(name="PW-INSP-A", inspection_date=date(2026, 10, 10))
        self._inspection(
            name="PW-INSP-B",
            inspection_date=date(2026, 10, 11),
            result="action",
        ).action_confirm()
        self.station.invalidate_recordset()
        self.assertEqual(self.station.inspection_count, 2)
        self.assertEqual(self.station.open_finding_count, 1)
        found = self.env["pest.station"].search([
            ("open_finding_count", ">", 0),
            ("id", "=", self.station.id),
        ])
        self.assertIn(self.station, found)

    def test_08_company_isolation(self):
        foreign = self.env["pest.station"].with_company(
            self.other_company).sudo().create({
            "name": "PestWatch Foreign Station",
            "code": "PW-ST-FRN",
            "location": "Remote",
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self.env["pest.station"].create({
            "name": "PestWatch Local Station",
            "code": "PW-ST-LOC",
            "location": "Local",
        })
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)

    def test_09_unique_station_code_per_company(self):
        with self.assertRaises(Exception):
            self.env["pest.station"].create({
                "name": "PestWatch Duplicate",
                "code": "PW-ST-001",
                "location": "Elsewhere",
            })
