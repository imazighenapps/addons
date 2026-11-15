# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSafetyDrillLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "sdl-manager",
            ["safety_drill_log.group_safetydrilll_user"])
        cls.outsider = cls._user("sdl-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _drill(self, **vals):
        data = {
            "name": vals.pop("name", "SDL-TEST"),
            "drill_date": fields.Date.context_today(self.env.user),
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["safety.drill.log"].create(data)

    def test_01_create_drill(self):
        rec = self._drill()
        self.assertEqual(rec.state, "draft")

    def test_02_complete_flow(self):
        rec = self._drill()
        rec.action_done()
        self.assertEqual(rec.state, "done")

    def test_03_cancel_and_reset(self):
        rec = self._drill()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._drill()
        rec.action_done()
        with self.assertRaises(UserError):
            rec.action_done()
        rec = self._drill(name="SDL-TEST-2")
        rec.action_cancel()
        with self.assertRaises(UserError):
            rec.action_cancel()

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["safety.drill.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "company_id": self.env.company.id,
                })
        rec = self._drill(name="SDL-ACC")
        rec.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "SDL B"})
        foreign = self.env["safety.drill.log"].create({
            "name": "SDL-FOREIGN",
            "company_id": company_b.id,
        })
        visible = self.env["safety.drill.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
