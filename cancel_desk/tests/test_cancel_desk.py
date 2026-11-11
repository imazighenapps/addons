# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCancelDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "CancelDesk Other Company"})
        cls.partner = cls.env["res.partner"].create({
            "name": "CancelDesk Test Customer"})

    def _log(self, **values):
        defaults = {
            "document": "CancelDesk Test Order SO-789",
            "partner_id": self.partner.id,
            "amount": 7400.0,
            "decided_on": date(2026, 5, 11),
            "reason": "price",
        }
        defaults.update(values)
        return self.env["cancel.desk.log"].create(defaults)

    def _recovery(self, log, **values):
        defaults = {
            "log_id": log.id,
            "new_ref": "CancelDesk Test Order SO-801",
            "amount": 3600.0,
            "recovered_on": date(2026, 9, 11),
        }
        defaults.update(values)
        return self.env["cancel.desk.recovery"].create(defaults)

    def test_01_log_defaults(self):
        log = self._log()
        self.assertTrue(log.name.startswith("CND/"))
        self.assertEqual(log.state, "logged")
        self.assertEqual(log.company_id, self.env.company)
        self.assertEqual(log.amount, 7400.0)
        self.assertEqual(log.decided_by, self.env.user)
        self.assertEqual(log.recovery_count, 0)
        self.assertAlmostEqual(log.recovered_total, 0.0, places=2)
        self.assertFalse(log.fully_recovered)
        self.assertFalse(log.written_off)

    def test_02_write_off_closes_the_file(self):
        log = self._log()
        self.assertTrue(log.action_write_off())
        self.assertEqual(log.state, "written_off")
        self.assertTrue(log.written_off)
        with self.assertRaises(UserError):
            log.action_write_off()

    def test_03_recoveries_add_up(self):
        log = self._log()
        first = self._recovery(log,
                               new_ref="CancelDesk Test Order SO-801")
        second = self._recovery(log,
                                new_ref="CancelDesk Test Order SO-802",
                                amount=3800.0,
                                recovered_on=date(2026, 9, 24))
        log.invalidate_recordset()
        self.assertEqual(first.amount, 3600.0)
        self.assertEqual(second.amount, 3800.0)
        self.assertEqual(log.recovery_count, 2)
        self.assertAlmostEqual(log.recovered_total, 7400.0, places=2)
        self.assertTrue(log.fully_recovered)
        self.assertEqual(log.state, "recovered")

    def test_04_partial_recovery_stays_logged(self):
        log = self._log()
        self._recovery(log)
        log.invalidate_recordset()
        self.assertAlmostEqual(log.recovered_total, 3600.0, places=2)
        self.assertFalse(log.fully_recovered)
        self.assertEqual(log.state, "logged")
        self.assertTrue(log.action_write_off())
        self.assertEqual(log.state, "written_off")

    def test_05_recovery_needs_an_open_cancellation(self):
        log = self._log()
        log.action_write_off()
        with self.assertRaises(UserError):
            self._recovery(log)
        recovered = self._log(document="CancelDesk Test Order SO-810")
        self._recovery(recovered, amount=7400.0)
        recovered.invalidate_recordset()
        self.assertEqual(recovered.state, "recovered")
        with self.assertRaises(UserError):
            self._recovery(recovered,
                           new_ref="CancelDesk Test Order SO-811",
                           amount=100.0)

    def test_06_reopen_rules(self):
        written = self._log(document="CancelDesk Test Order SO-820")
        written.action_write_off()
        self.assertTrue(written.action_reopen())
        self.assertEqual(written.state, "logged")
        with self.assertRaises(UserError):
            written.action_reopen()
        recovered = self._log(document="CancelDesk Test Order SO-821")
        self._recovery(recovered, amount=7400.0)
        recovered.invalidate_recordset()
        with self.assertRaises(UserError):
            recovered.action_reopen()
        self.assertEqual(recovered.state, "recovered")

    def test_07_constraints(self):
        with self.assertRaises(ValidationError):
            self._log(amount=-10.0)
        log = self._log()
        with self.assertRaises(ValidationError):
            self._recovery(log, amount=0.0)
        with self.assertRaises(ValidationError):
            self._recovery(log, amount=-50.0)
        with self.assertRaises(ValidationError):
            self._recovery(log, recovered_on=date(2026, 5, 2))
        with self.assertRaises(ValidationError):
            self._log(decided_on=fields.Date.context_today(log)
                      + timedelta(days=1))

    def test_08_recovery_lines_locked_when_closed(self):
        log = self._log()
        recovery = self._recovery(log)
        log.action_write_off()
        with self.assertRaises(UserError):
            recovery.write({"amount": 5000.0})
        self.assertEqual(recovery.amount, 3600.0)

    def test_09_search_filters_and_counters(self):
        fully = self._log(document="CancelDesk Test Order SO-820")
        self._recovery(fully,
                       new_ref="CancelDesk Test Order SO-821")
        self._recovery(fully,
                       new_ref="CancelDesk Test Order SO-822",
                       amount=3800.0,
                       recovered_on=date(2026, 9, 24))
        logged = self._log(document="CancelDesk Test Order SO-823",
                           reason="delivery")
        logs = self.env["cancel.desk.log"]
        self.assertIn(fully, logs.search(
            [("fully_recovered", "=", True)]))
        self.assertNotIn(logged, logs.search(
            [("fully_recovered", "=", True)]))
        self.assertIn(fully, logs.search(
            [("recovery_count", ">", 0)]))
        self.assertNotIn(logged, logs.search(
            [("recovery_count", ">", 0)]))
        self.assertIn(logged, logs.search(
            [("decided_on", ">=", "2026-01-01")]))

    def test_10_company_isolation(self):
        foreign = self.env["cancel.desk.log"].with_company(
            self.other_company).sudo().create({
            "document": "CancelDesk Test Order SO-FOR",
            "amount": 1500.0,
            "decided_on": date(2026, 5, 11),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._log()
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
