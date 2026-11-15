# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestItAssetLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "ial-manager",
            ["it_asset_log.group_itassetlog_user"])
        cls.outsider = cls._user("ial-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _asset(self, **vals):
        data = {
            "name": vals.pop("name", "IT-TEST-001"),
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["it.asset.log"].create(data)

    def test_01_create_asset(self):
        rec = self._asset()
        self.assertEqual(rec.state, "draft")

    def test_02_assign_repair_spare_flow(self):
        rec = self._asset()
        rec.action_assign()
        self.assertEqual(rec.state, "in_use")
        rec.action_repair()
        self.assertEqual(rec.state, "repair")
        rec.action_spare()
        self.assertEqual(rec.state, "spare")
        rec.action_assign()
        self.assertEqual(rec.state, "in_use")

    def test_03_retire_and_reset(self):
        rec = self._asset()
        rec.action_assign()
        rec.action_spare()
        rec.action_retire()
        self.assertEqual(rec.state, "retired")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._asset()
        with self.assertRaises(UserError):
            rec.action_repair()
        rec.action_assign()
        with self.assertRaises(UserError):
            rec.action_assign()

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["it.asset.log"].with_user(
                self.outsider).create({
                    "name": "NO-ACC",
                    "company_id": self.env.company.id,
                })
        rec = self._asset(name="IT-ACC")
        rec.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "IAL B"})
        foreign = self.env["it.asset.log"].create({
            "name": "IT-FOREIGN",
            "company_id": company_b.id,
        })
        visible = self.env["it.asset.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
