# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestContractExpiryLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Contract Partner"})
        cls.today = fields.Date.context_today(cls.env.user)
        cls.manager = cls._user(
            "ctr-manager", ["contract_expiry_log.group_contractexpi_user"])
        cls.outsider = cls._user("ctr-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _contract(self, **vals):
        data = {
            "name": vals.pop("name", "CTR-TEST"),
            "partner_id": self.partner.id,
            "end_date": self.today + timedelta(days=30),
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["contract.expiry.log"].create(data)

    def test_01_create_and_days_to_expiry(self):
        contract = self._contract(end_date=self.today + timedelta(days=10))
        self.assertEqual(contract.days_to_expiry, 10)
        self.assertEqual(contract.state, "draft")

    def test_02_state_flow(self):
        contract = self._contract()
        contract.action_activate()
        self.assertEqual(contract.state, "active")
        contract.action_mark_expiring()
        self.assertEqual(contract.state, "expiring")
        contract.action_activate()
        contract.action_renew()
        self.assertEqual(contract.state, "renewed")
        contract.action_reset_draft()
        self.assertEqual(contract.state, "draft")
        contract.action_activate()
        contract.action_close()
        self.assertEqual(contract.state, "closed")

    def test_03_invalid_state_transitions(self):
        contract = self._contract()
        with self.assertRaises(UserError):
            contract.action_mark_expiring()
        contract.action_activate()
        contract.action_close()
        with self.assertRaises(UserError):
            contract.action_close()

    def test_04_end_before_start_is_refused(self):
        with self.assertRaises(ValidationError):
            self._contract(
                start_date=self.today,
                end_date=self.today - timedelta(days=1),
            )

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["contract.expiry.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "partner_id": self.partner.id,
                    "end_date": self.today + timedelta(days=5),
                    "company_id": self.env.company.id,
                })
        contract = self._contract(name="CTR-ACC")
        contract.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "CTR B"})
        foreign = self.env["contract.expiry.log"].create({
            "name": "CTR-FOREIGN",
            "partner_id": self.partner.id,
            "end_date": self.today + timedelta(days=5),
            "company_id": company_b.id,
        })
        visible = self.env["contract.expiry.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
