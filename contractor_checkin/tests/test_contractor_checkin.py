# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestContractorCheckin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.host = cls.env["hr.employee"].create({"name": "Host Employee"})
        cls.manager = cls._user(
            "checkin-manager", ["contractor_checkin.group_contractorch_user"])
        cls.outsider = cls._user(
            "checkin-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _check(self):
        return self.env["contractor.checkin"].create({
            "contractor_name": "John Contractor",
            "contractor_company": "Ext Co",
            "host_id": self.host.id,
            "purpose": "Maintenance",
            "company_id": self.env.company.id,
        })

    def test_01_checkout(self):
        c = self._check()
        self.assertEqual(c.state, "on_site")
        c.action_checkout()
        self.assertEqual(c.state, "checked_out")
        self.assertTrue(c.checkout_time)

    def test_02_cancel(self):
        c = self._check()
        c.action_cancel()
        self.assertEqual(c.state, "cancelled")
        c.action_reset()
        self.assertEqual(c.state, "on_site")

    def test_03_state_guards(self):
        c = self._check()
        c.action_checkout()
        with self.assertRaises(UserError):
            c.action_checkout()
        with self.assertRaises(UserError):
            c.action_cancel()

    def test_04_time_validation(self):
        now = fields.Datetime.now()
        with self.assertRaises(ValidationError):
            self.env["contractor.checkin"].create({
                "contractor_name": "Bad",
                "purpose": "x",
                "checkin_time": now,
                "checkout_time": now - timedelta(hours=1),
                "company_id": self.env.company.id,
            })

    def test_05_access_control(self):
        c = self._check()
        with self.assertRaises(Exception):
            self.env["contractor.checkin"].with_user(self.outsider).create({
                "contractor_name": "No",
                "purpose": "x",
                "company_id": self.env.company.id,
            })
        c.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Check B"})
        foreign = self.env["contractor.checkin"].create({
            "contractor_name": "Foreign",
            "purpose": "x",
            "company_id": company_b.id,
        })
        visible = self.env["contractor.checkin"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
