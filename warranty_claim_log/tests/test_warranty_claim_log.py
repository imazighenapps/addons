# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWarrantyClaimLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Claim Customer"})
        cls.manager = cls._user(
            "wcl-manager",
            ["warranty_claim_log.group_warrantyclai_user"])
        cls.outsider = cls._user("wcl-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _claim(self, **vals):
        data = {
            "name": vals.pop("name", "WCL-TEST"),
            "partner_id": self.partner.id,
            "claim_date": fields.Date.context_today(self.env.user),
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["warranty.claim.log"].create(data)

    def test_01_create_claim(self):
        rec = self._claim()
        self.assertEqual(rec.state, "draft")

    def test_02_state_flow_approved_resolved(self):
        rec = self._claim()
        rec.action_review()
        self.assertEqual(rec.state, "review")
        rec.action_approve()
        self.assertEqual(rec.state, "approved")
        rec.action_resolve()
        self.assertEqual(rec.state, "resolved")

    def test_03_reject_and_reset(self):
        rec = self._claim()
        rec.action_review()
        rec.action_reject()
        self.assertEqual(rec.state, "rejected")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._claim()
        with self.assertRaises(UserError):
            rec.action_approve()
        rec.action_review()
        with self.assertRaises(UserError):
            rec.action_resolve()

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["warranty.claim.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "partner_id": self.partner.id,
                    "company_id": self.env.company.id,
                })
        rec = self._claim(name="WCL-ACC")
        rec.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "WCL B"})
        foreign = self.env["warranty.claim.log"].create({
            "name": "WCL-FOREIGN",
            "partner_id": self.partner.id,
            "company_id": company_b.id,
        })
        visible = self.env["warranty.claim.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
