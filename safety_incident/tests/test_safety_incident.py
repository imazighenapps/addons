# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSafetyIncident(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Safety Employee"})
        cls.manager = cls._user(
            "safety-manager", ["safety_incident.group_safetyincide_user"])
        cls.outsider = cls._user(
            "safety-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _inc(self):
        return self.env["safety.incident"].create({
            "location": "Warehouse",
            "incident_type": "near_miss",
            "severity": "medium",
            "employee_id": self.employee.id,
            "description": "Pallet nearly fell.",
            "company_id": self.env.company.id,
        })

    def test_01_flow_report_progress_close(self):
        i = self._inc()
        i.action_report()
        self.assertEqual(i.state, "reported")
        i.action_start()
        self.assertEqual(i.state, "in_progress")
        i.action_close()
        self.assertEqual(i.state, "closed")
        i.action_reset()
        self.assertEqual(i.state, "draft")

    def test_02_close_from_reported(self):
        i = self._inc()
        i.action_report()
        i.action_close()
        self.assertEqual(i.state, "closed")

    def test_03_state_guards(self):
        i = self._inc()
        with self.assertRaises(UserError):
            i.action_start()
        with self.assertRaises(UserError):
            i.action_close()
        i.action_report()
        with self.assertRaises(UserError):
            i.action_report()

    def test_04_access_control(self):
        i = self._inc()
        with self.assertRaises(Exception):
            self.env["safety.incident"].with_user(self.outsider).create({
                "location": "X",
                "incident_type": "other",
                "severity": "low",
                "description": "No",
                "company_id": self.env.company.id,
            })
        i.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Safety B"})
        foreign = self.env["safety.incident"].create({
            "location": "B",
            "incident_type": "hazard",
            "severity": "low",
            "description": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["safety.incident"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
