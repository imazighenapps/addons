# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSla(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel = cls.env["discuss.channel"].create({
            "name": "Support Internal", "channel_type": "channel",
        })
        cls.policy = cls.env.ref("discuss_sla_handover.policy_standard")
        cls.urgent = cls.env.ref("discuss_sla_handover.policy_urgent")

    def _case(self, policy, opened_ago_hours=0.0):
        opened = fields.Datetime.now() - timedelta(hours=opened_ago_hours)
        return self.env["discuss.sla.case"].create({
            "channel_id": self.channel.id,
            "policy_id": policy.id,
            "open_date": opened,
        })

    def test_01_seed_policies(self):
        # do not assert a global count: an operator adding their own
        # policy must not break the module's test suite
        self.assertLess(
            self.urgent.first_response_hours, self.policy.first_response_hours,
            "The urgent policy must react faster than the standard one.")
        self.assertLess(
            self.urgent.resolution_hours, self.policy.resolution_hours)

    def test_02_sequence_and_deadlines(self):
        case = self._case(self.policy)
        self.assertTrue(case.name.startswith("SLA-"))
        span = case.resolution_deadline - case.open_date
        self.assertAlmostEqual(span.total_seconds() / 3600.0, 24.0, places=1)
        self.assertEqual(case.state, "open")

    def test_03_response_and_resolve(self):
        case = self._case(self.policy)
        case.action_set_response()
        self.assertEqual(case.state, "responded")
        self.assertTrue(case.first_response_date)
        case.action_resolve()
        self.assertEqual(case.state, "resolved")
        self.assertTrue(case.close_date)
        case.action_reopen()
        self.assertEqual(case.state, "open")
        self.assertFalse(case.close_date)

    def test_04_breach_detected(self):
        case = self._case(self.urgent, opened_ago_hours=6.0)
        case.invalidate_recordset(["level", "breach"])
        self.assertTrue(case.breach)
        self.assertEqual(case.level, "breach")
        # resolving late keeps the breach recorded
        case.action_resolve()
        case.invalidate_recordset(["breach"])
        self.assertTrue(case.breach)

    def test_05_on_track_case(self):
        case = self._case(self.policy, opened_ago_hours=1.0)
        case.invalidate_recordset(["level"])
        self.assertEqual(case.level, "ok")
        self.assertFalse(case.breach)

    def test_06_handover_flow(self):
        log = self.env["discuss.handover.log"].create({
            "to_user_id": self.env.uid,
            "summary": "Two open cases, one blocked on supplier.",
            "pending_actions": "Chase supplier, confirm backorder.",
            # scope the snapshot to our own channel, otherwise it counts
            # every unresolved case in the database and the assertion
            # depends on pre-existing data
            "channel_ids": [(6, 0, self.channel.ids)],
        })
        self.assertTrue(log.name.startswith("HO-"))
        self._case(self.policy)
        log.action_snapshot_cases()
        self.assertEqual(log.open_cases, 1)
        log.action_give()
        self.assertEqual(log.state, "given")
        log.action_receive()
        self.assertEqual(log.state, "received")

    def test_07_cron_runs(self):
        self._case(self.urgent, opened_ago_hours=6.0)
        self.assertTrue(self.env["discuss.sla.case"]._cron_check())
        self.assertTrue(self.env["discuss.channel"]._cron_archive_idle() >= 0)