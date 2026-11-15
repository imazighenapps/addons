# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPestControlLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "pcl-manager",
            ["pest_control_log.group_pestcontroll_user"])
        cls.outsider = cls._user("pcl-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _intervention(self, **vals):
        data = {
            "name": vals.pop("name", "PCL-TEST"),
            "intervention_date": fields.Date.context_today(self.env.user),
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["pest.control.log"].create(data)

    def test_01_create_intervention(self):
        rec = self._intervention()
        self.assertEqual(rec.state, "draft")

    def test_02_state_flow(self):
        rec = self._intervention()
        rec.action_schedule()
        self.assertEqual(rec.state, "scheduled")
        rec.action_done()
        self.assertEqual(rec.state, "done")

    def test_03_cancel_and_reset(self):
        rec = self._intervention()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._intervention()
        with self.assertRaises(UserError):
            rec.action_done()
        rec.action_schedule()
        rec.action_done()
        with self.assertRaises(UserError):
            rec.action_cancel()

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["pest.control.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "company_id": self.env.company.id,
                })
        rec = self._intervention(name="PCL-ACC")
        rec.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "PCL B"})
        foreign = self.env["pest.control.log"].create({
            "name": "PCL-FOREIGN",
            "company_id": company_b.id,
        })
        visible = self.env["pest.control.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
