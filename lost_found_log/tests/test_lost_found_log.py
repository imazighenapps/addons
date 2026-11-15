# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLostFound(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "lostfound-manager", ["lost_found_log.group_lostfoundlog_user"])
        cls.outsider = cls._user(
            "lostfound-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _item(self):
        return self.env["lost.found.item"].create({
            "description": "Blue umbrella",
            "location_found": "Lobby",
            "company_id": self.env.company.id,
        })

    def test_01_flow_claim_return(self):
        i = self._item()
        self.assertEqual(i.state, "found")
        i.action_claim()
        self.assertEqual(i.state, "claimed")
        i.action_return()
        self.assertEqual(i.state, "returned")
        self.assertTrue(i.date_returned)

    def test_02_dispose(self):
        i = self._item()
        i.action_dispose()
        self.assertEqual(i.state, "disposed")

    def test_03_invalid_transitions(self):
        i = self._item()
        i.action_return()
        with self.assertRaises(UserError):
            i.action_dispose()

    def test_04_access_control(self):
        i = self._item()
        with self.assertRaises(Exception):
            self.env["lost.found.item"].with_user(self.outsider).create({
                "description": "No",
                "location_found": "X",
                "company_id": self.env.company.id,
            })
        i.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "LF B"})
        foreign = self.env["lost.found.item"].create({
            "description": "Foreign",
            "location_found": "B",
            "company_id": company_b.id,
        })
        visible = self.env["lost.found.item"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
