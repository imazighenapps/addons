# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHazardReportLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "hrl-manager",
            ["hazard_report_log.group_hazardreport_user"])
        cls.outsider = cls._user("hrl-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _report(self, **vals):
        data = {
            "name": vals.pop("name", "HRL-TEST"),
            "report_date": fields.Date.context_today(self.env.user),
            "description": "Test hazard",
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["hazard.report.log"].create(data)

    def test_01_create_report(self):
        rec = self._report()
        self.assertEqual(rec.state, "draft")

    def test_02_resolve_flow(self):
        rec = self._report()
        rec.action_report()
        self.assertEqual(rec.state, "reported")
        rec.action_start()
        self.assertEqual(rec.state, "progress")
        rec.action_resolve()
        self.assertEqual(rec.state, "resolved")
        self.assertTrue(rec.resolution_date)

    def test_03_dismiss_and_reset(self):
        rec = self._report()
        rec.action_report()
        rec.action_dismiss()
        self.assertEqual(rec.state, "dismissed")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._report()
        with self.assertRaises(UserError):
            rec.action_start()
        rec.action_report()
        with self.assertRaises(UserError):
            rec.action_resolve()

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["hazard.report.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "description": "No access",
                    "company_id": self.env.company.id,
                })
        rec = self._report(name="HRL-ACC")
        rec.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "HRL B"})
        foreign = self.env["hazard.report.log"].create({
            "name": "HRL-FOREIGN",
            "description": "Foreign hazard",
            "company_id": company_b.id,
        })
        visible = self.env["hazard.report.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
