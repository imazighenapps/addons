# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPermitToWorkLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contractor = cls.env["res.partner"].create({"name": "Permit Contractor"})
        cls.manager = cls._user(
            "ptw-manager",
            ["permit_to_work_log.group_permittowork_user"])
        cls.outsider = cls._user("ptw-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _permit(self, **vals):
        data = {
            "name": vals.pop("name", "PTW-TEST"),
            "permit_type": "general",
            "location": "Test Site",
            "contractor_id": self.contractor.id,
            "description": "Test work description.",
            "safety_measures": "Test safety measures.",
            "valid_from": self.today,
            "valid_to": self.today + timedelta(days=1),
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["permit.to.work.log"].create(data)

    def test_01_create_permit(self):
        rec = self._permit()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.name)

    def test_02_full_workflow(self):
        rec = self._permit()
        rec.action_submit()
        self.assertEqual(rec.state, "requested")
        rec.action_approve()
        self.assertEqual(rec.state, "approved")
        self.assertEqual(rec.approver_id, self.env.user)
        rec.action_activate()
        self.assertEqual(rec.state, "active")
        rec.action_close()
        self.assertEqual(rec.state, "closed")

    def test_03_invalid_transitions(self):
        rec = self._permit()
        with self.assertRaises(UserError):
            rec.action_approve()
        with self.assertRaises(UserError):
            rec.action_activate()
        with self.assertRaises(UserError):
            rec.action_close()
        rec.action_submit()
        with self.assertRaises(UserError):
            rec.action_submit()

    def test_04_date_constraint(self):
        with self.assertRaises(ValidationError):
            self._permit(valid_to=self.today - timedelta(days=1))

    def test_05_cancel_and_reset(self):
        rec = self._permit()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["permit.to.work.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "location": "No",
                    "description": "No",
                    "valid_from": self.today,
                    "valid_to": self.today,
                    "company_id": self.env.company.id,
                })
        rec = self._permit(name="PTW-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "PTW B"})
        foreign = self.env["permit.to.work.log"].create({
            "name": "PTW-FOREIGN",
            "location": "Foreign",
            "description": "Foreign",
            "valid_from": self.today,
            "valid_to": self.today + timedelta(days=1),
            "company_id": company_b.id,
        })
        visible = self.env["permit.to.work.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
