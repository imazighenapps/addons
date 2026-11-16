# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAssetDisposalLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "adl-manager",
            ["asset_disposal_log.group_assetdisposa_user"])
        cls.outsider = cls._user("adl-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _record(self, **vals):
        data = {
            "name": vals.pop("name", "ADL-TEST"),
            "asset_ref": "IT-TEST",
            "asset_name": "Test Asset",
            "asset_category": "it",
            "disposal_method": "scrap",
            "disposal_date": self.today,
            "acquisition_value": 500.0,
            "residual_value": 0.0,
            "reason": "End of life.",
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["asset.disposal.log"].create(data)

    def test_01_create_request(self):
        rec = self._record()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.name)

    def test_02_full_workflow(self):
        rec = self._record()
        rec.action_submit()
        self.assertEqual(rec.state, "submitted")
        rec.action_approve()
        self.assertEqual(rec.state, "approved")
        self.assertEqual(rec.approver_id, self.env.user)
        rec.action_dispose()
        self.assertEqual(rec.state, "disposed")

    def test_03_submit_requires_reason(self):
        rec = self._record(reason=False)
        with self.assertRaises(UserError):
            rec.action_submit()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._record()
        with self.assertRaises(UserError):
            rec.action_approve()
        with self.assertRaises(UserError):
            rec.action_dispose()
        rec.action_submit()
        with self.assertRaises(UserError):
            rec.action_submit()

    def test_05_constraints(self):
        with self.assertRaises(ValidationError):
            self._record(acquisition_value=-1.0)
        with self.assertRaises(ValidationError):
            self._record(residual_value=-1.0)

    def test_06_cancel_and_reset(self):
        rec = self._record()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_07_access_control(self):
        with self.assertRaises(Exception):
            self.env["asset.disposal.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "asset_ref": "NO",
                    "asset_name": "No",
                    "company_id": self.env.company.id,
                })
        rec = self._record(name="ADL-ACC")
        rec.with_user(self.manager).read()

    def test_08_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "ADL B"})
        foreign = self.env["asset.disposal.log"].create({
            "name": "ADL-FOREIGN",
            "asset_ref": "IT-B",
            "asset_name": "Foreign Asset",
            "company_id": company_b.id,
        })
        visible = self.env["asset.disposal.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
