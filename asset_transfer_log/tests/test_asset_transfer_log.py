# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAssetTransferLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env["maintenance.equipment"].create({
            "name": "Test Equipment",
        })
        cls.manager = cls._user(
            "atl-manager",
            ["asset_transfer_log.group_assettransfe_user"])
        cls.outsider = cls._user("atl-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _transfer(self, **vals):
        data = {
            "name": vals.pop("name", "ATL-TEST"),
            "equipment_id": self.equipment.id,
            "transfer_date": fields.Date.context_today(self.env.user),
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["asset.transfer.log"].create(data)

    def test_01_create_transfer(self):
        rec = self._transfer()
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.equipment_id, self.equipment)

    def test_02_state_flow(self):
        rec = self._transfer()
        rec.action_start()
        self.assertEqual(rec.state, "progress")
        rec.action_done()
        self.assertEqual(rec.state, "done")

    def test_03_cancel_and_reset(self):
        rec = self._transfer()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._transfer()
        with self.assertRaises(UserError):
            rec.action_done()
        rec.action_start()
        rec.action_done()
        with self.assertRaises(UserError):
            rec.action_cancel()

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["asset.transfer.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "equipment_id": self.equipment.id,
                    "company_id": self.env.company.id,
                })
        rec = self._transfer(name="ATL-ACC")
        rec.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "ATL B"})
        foreign = self.env["asset.transfer.log"].create({
            "name": "ATL-FOREIGN",
            "equipment_id": self.equipment.id,
            "company_id": company_b.id,
        })
        visible = self.env["asset.transfer.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
