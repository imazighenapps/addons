# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVisitorBadgeLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.badge = cls.env["visitor.badge"].create({
            "name": "VB-001", "company_id": cls.env.company.id,
        })
        cls.host = cls.env["hr.employee"].create({"name": "Host"})
        cls.manager = cls._user(
            "vbadge-manager", ["visitor_badge_log.group_visitorbadge_user"])
        cls.outsider = cls._user(
            "vbadge-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _iss(self):
        return self.env["visitor.badge.issuance"].create({
            "badge_id": self.badge.id,
            "visitor_name": "John Visitor",
            "host_id": self.host.id,
            "company_id": self.env.company.id,
        })

    def test_01_return(self):
        i = self._iss()
        i.action_return()
        self.assertEqual(i.state, "returned")
        self.assertTrue(i.return_time)

    def test_02_lost(self):
        i = self._iss()
        i.action_lost()
        self.assertEqual(i.state, "lost")

    def test_03_invalid_transitions(self):
        i = self._iss()
        i.action_return()
        with self.assertRaises(UserError):
            i.action_lost()

    def test_04_time_validation(self):
        now = fields.Datetime.now()
        with self.assertRaises(ValidationError):
            self.env["visitor.badge.issuance"].create({
                "badge_id": self.badge.id,
                "visitor_name": "Bad",
                "issue_time": now,
                "return_time": now - timedelta(hours=1),
                "company_id": self.env.company.id,
            })

    def test_05_access_control(self):
        i = self._iss()
        with self.assertRaises(Exception):
            self.env["visitor.badge.issuance"].with_user(self.outsider).create({
                "badge_id": self.badge.id,
                "visitor_name": "No",
                "company_id": self.env.company.id,
            })
        i.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "VB B"})
        badge_b = self.env["visitor.badge"].create({"name": "VB-B", "company_id": company_b.id})
        foreign = self.env["visitor.badge.issuance"].create({
            "badge_id": badge_b.id,
            "visitor_name": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["visitor.badge.issuance"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
