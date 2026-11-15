# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVisitorParcelLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "vpl-manager",
            ["visitor_parcel_log.group_visitorparce_user"])
        cls.outsider = cls._user("vpl-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _parcel(self, **vals):
        data = {
            "name": vals.pop("name", "VPL-TEST"),
            "arrival_date": fields.Datetime.now(),
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["visitor.parcel.log"].create(data)

    def test_01_create_parcel(self):
        rec = self._parcel()
        self.assertEqual(rec.state, "received")

    def test_02_notify_and_collect(self):
        rec = self._parcel()
        rec.action_notify()
        self.assertEqual(rec.state, "notified")
        rec.action_collect()
        self.assertEqual(rec.state, "collected")
        self.assertTrue(rec.collected_date)

    def test_03_return_and_reset(self):
        rec = self._parcel()
        rec.action_return()
        self.assertEqual(rec.state, "returned")
        rec.action_reset_received()
        self.assertEqual(rec.state, "received")

    def test_04_invalid_transitions(self):
        rec = self._parcel()
        with self.assertRaises(UserError):
            rec.action_reset_received()
        rec.action_collect()
        with self.assertRaises(UserError):
            rec.action_return()

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["visitor.parcel.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "company_id": self.env.company.id,
                })
        rec = self._parcel(name="VPL-ACC")
        rec.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "VPL B"})
        foreign = self.env["visitor.parcel.log"].create({
            "name": "VPL-FOREIGN",
            "company_id": company_b.id,
        })
        visible = self.env["visitor.parcel.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
