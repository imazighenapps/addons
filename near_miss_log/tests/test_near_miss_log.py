# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNearMissLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reporter = cls.env["hr.employee"].create({"name": "Near Miss Reporter"})
        cls.manager = cls._user(
            "nml-manager",
            ["near_miss_log.group_nearmisslog_user"])
        cls.outsider = cls._user("nml-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _report(self, **vals):
        data = {
            "name": vals.pop("name", "NML-TEST"),
            "event_date": self.today,
            "location": "Test Site",
            "description": "Test near miss description.",
            "severity": "low",
            "reporter_id": self.reporter.id,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["near.miss.log"].create(data)

    def test_01_create_report(self):
        rec = self._report()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.name)

    def test_02_full_workflow(self):
        rec = self._report(corrective_action="Test action.")
        rec.action_report()
        self.assertEqual(rec.state, "reported")
        rec.action_investigate()
        self.assertEqual(rec.state, "investigating")
        self.assertEqual(rec.responsible_id, self.env.user)
        rec.action_close()
        self.assertEqual(rec.state, "closed")

    def test_03_investigate_requires_action(self):
        rec = self._report()
        rec.action_report()
        with self.assertRaises(UserError):
            rec.action_investigate()
        self.assertEqual(rec.state, "reported")

    def test_04_invalid_transitions(self):
        rec = self._report()
        with self.assertRaises(UserError):
            rec.action_investigate()
        with self.assertRaises(UserError):
            rec.action_close()
        rec.action_report()
        with self.assertRaises(UserError):
            rec.action_report()

    def test_05_cancel_and_reset(self):
        rec = self._report()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["near.miss.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "location": "No",
                    "description": "No",
                    "company_id": self.env.company.id,
                })
        rec = self._report(name="NML-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "NML B"})
        foreign = self.env["near.miss.log"].create({
            "name": "NML-FOREIGN",
            "location": "Foreign",
            "description": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["near.miss.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
