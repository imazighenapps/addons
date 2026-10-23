# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBradford(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sick_type = cls.env["hr.leave.type"].create({
            "name": "Sick Test",
            "bradford_included": True,
            "bradford_code": "sickness_short",
            "requires_allocation": "no",
        })
        cls.vac_type = cls.env["hr.leave.type"].create({
            "name": "Vacation Test",
            "bradford_included": False,
            "requires_allocation": "no",
        })
        cls.employee = cls.env["hr.employee"].create({"name": "Demo Worker"})

    def _employee(self, name):
        return self.env["hr.employee"].create({"name": name})

    def _leave(self, emp, start_ago, days, ltype=None):
        start = date.today() - timedelta(days=start_ago)
        end = start + timedelta(days=days - 1)
        return self.env["hr.leave"].with_context(
            leave_skip_date_check=True).create({
            "employee_id": emp.id,
            "holiday_status_id": (ltype or self.sick_type).id,
            "request_date_from": start,
            "request_date_to": end,
            "date_from": "%s 08:00:00" % start,
            "date_to": "%s 18:00:00" % end,
            "number_of_days": float(days),
        })

    def test_01_formula(self):
        emp = self._employee("Worker One")
        for days_ago, days in [(300, 2), (200, 2)]:
            self._leave(emp, days_ago, days).write({"state": "validate"})
        # contiguous pair merges into a single spell
        self._leave(emp, 100, 1).write({"state": "validate"})
        self._leave(emp, 99, 1).write({"state": "validate"})
        emp._bradford_rebuild_spells()
        emp._compute_bradford()
        spells = self.env["bradford.spell"].search([("employee_id", "=", emp.id)])
        self.assertEqual(len(spells), 3)
        self.assertEqual(emp.bradford_s, 3)
        expected_d = round(sum(spells.mapped("days")))
        self.assertEqual(emp.bradford_score, 9 * expected_d)

    def test_02_excluded_types_ignored(self):
        emp = self._employee("Worker Two")
        self._leave(emp, 50, 5, self.vac_type).write({"state": "validate"})
        emp._bradford_rebuild_spells()
        spells = self.env["bradford.spell"].search(
            [("employee_id", "=", emp.id)])
        self.assertEqual(len(spells), 0)

    def test_03_threshold_band(self):
        band = self.env["bradford.threshold"]._band_for(250)
        self.assertIn("200", band)

    def test_04_alert_created(self):
        emp = self._employee("Worker Four")
        for days_ago, days in [(300, 2), (200, 2), (100, 2), (60, 2), (30, 2)]:
            self._leave(emp, days_ago, days).write({"state": "validate"})
        self.env["bradford.threshold"]._cron_recompute_all()
        emp.invalidate_recordset()
        spells = self.env["bradford.spell"].search([("employee_id", "=", emp.id)])
        self.assertEqual(len(spells), 5)
        self.assertEqual(emp.bradford_score, 25 * int(round(sum(spells.mapped("days")))))
        alerts = self.env["bradford.alert"].search(
            [("employee_id", "=", emp.id)])
        self.assertTrue(alerts)

    def test_05_rtw(self):
        emp = self._employee("Worker Five")
        leave = self._leave(emp, 5, 2)
        leave.write({"state": "validate"})
        rtw = self.env["hr.rtw.interview"].create({
            "employee_id": emp.id, "leave_id": leave.id,
            "declared_reason": "Back to work, workplace adjustments discussed.",
            "fitness_confirmed": True,
        })
        rtw.action_done()
        self.assertEqual(rtw.state, "done")
        self.assertNotIn("flu", (rtw.declared_reason or "").lower())

    def test_06_seed_thresholds(self):
        self.assertEqual(len(self.env["bradford.threshold"].search([])), 4)
