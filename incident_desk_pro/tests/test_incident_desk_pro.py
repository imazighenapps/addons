# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIncidentDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "IncidentDesk Other Company"})
        cls.incident = cls.env["ehs.incident"].create({
            "title": "IncidentDesk Test Fall",
            "type": "near_miss",
            "severity": "medium",
            "location": "Warehouse 2, loading bay",
            "description": "A pallet fell from the lower rack.",
        })

    def _action(self, incident=None, **values):
        defaults = {
            "incident_id": (incident or self.incident).id,
            "name": "IncidentDesk Test Action",
            "kind": "corrective",
        }
        defaults.update(values)
        return self.env["ehs.action"].create(defaults)

    def test_01_incident_defaults(self):
        self.assertEqual(self.incident.state, "draft")
        self.assertEqual(self.incident.type, "near_miss")
        self.assertEqual(self.incident.reported_by, self.env.user)
        self.assertEqual(self.incident.company_id, self.env.company)
        self.assertTrue(self.incident.name.startswith("INC "))
        self.assertTrue(self.incident.date_incident)

    def test_02_workflow_states(self):
        self.incident.action_investigate()
        self.assertEqual(self.incident.state, "investigating")
        with self.assertRaises(UserError):
            self.incident.action_investigate()
        self.incident.action_close()
        self.assertEqual(self.incident.state, "closed")
        self.assertTrue(self.incident.closed_date)

    def test_03_close_from_draft_is_refused(self):
        with self.assertRaises(UserError):
            self.incident.action_close()

    def test_04_close_is_blocked_by_open_actions(self):
        self.incident.action_investigate()
        self._action()
        self.assertEqual(self.incident.open_action_count, 1)
        with self.assertRaises(UserError):
            self.incident.action_close()
        self.assertEqual(self.incident.state, "investigating")

    def test_05_close_after_all_actions_are_done(self):
        self.incident.action_investigate()
        action = self._action()
        self._action(kind="preventive",
                     name="IncidentDesk Test Prevention")
        actions = self.incident.action_ids
        actions.action_done()
        self.assertEqual(self.incident.open_action_count, 0)
        self.assertTrue(action.done_date)
        self.assertTrue(self.incident.action_close())

    def test_06_reopens(self):
        self.incident.action_investigate()
        self.incident.action_close()
        self.assertTrue(self.incident.action_reopen())
        self.assertEqual(self.incident.state, "investigating")
        self.assertFalse(self.incident.closed_date)
        action = self._action()
        action.action_done()
        action.action_reopen()
        self.assertEqual(action.state, "todo")
        self.assertFalse(action.done_date)

    def test_07_action_defaults_and_counter(self):
        self.incident.action_investigate()
        self._action(kind="preventive")
        self.incident.invalidate_recordset()
        self.assertEqual(self.incident.total_action_count, 1)
        self.assertEqual(self.incident.open_action_count, 1)
        self.assertEqual(
            self.incident.action_ids.responsible_id, self.env.user)

    def test_08_company_isolation(self):
        foreign = self.env["ehs.incident"].sudo().create({
            "title": "IncidentDesk Test Foreign",
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        self.assertEqual(self.incident.company_id, self.env.company)
