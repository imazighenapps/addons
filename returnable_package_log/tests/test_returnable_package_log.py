# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReturnablePackageLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Packaging Partner"})
        cls.manager = cls._user(
            "rpl-manager",
            ["returnable_package_log.group_returnablepa_user"])
        cls.outsider = cls._user("rpl-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _movement(self, **vals):
        data = {
            "name": vals.pop("name", "RPL-TEST"),
            "partner_id": self.partner.id,
            "package_type": "pallet",
            "quantity": 10,
            "movement_type": "out",
            "movement_date": self.today,
            "due_date": self.today + timedelta(days=30),
            "deposit_amount": 150.0,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["returnable.package.log"].create(data)

    def test_01_create_movement(self):
        rec = self._movement()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.name)

    def test_02_send_and_return(self):
        rec = self._movement()
        rec.action_send()
        self.assertEqual(rec.state, "sent")
        rec.action_return()
        self.assertEqual(rec.state, "returned")
        self.assertTrue(rec.return_date)

    def test_03_mark_lost(self):
        rec = self._movement()
        rec.action_send()
        rec.action_mark_lost()
        self.assertEqual(rec.state, "lost")

    def test_04_invalid_transitions(self):
        rec = self._movement()
        with self.assertRaises(UserError):
            rec.action_return()
        with self.assertRaises(UserError):
            rec.action_mark_lost()
        rec.action_send()
        with self.assertRaises(UserError):
            rec.action_send()

    def test_05_constraints(self):
        with self.assertRaises(ValidationError):
            self._movement(quantity=0)
        with self.assertRaises(ValidationError):
            self._movement(deposit_amount=-5.0)
        with self.assertRaises(ValidationError):
            self._movement(due_date=self.today - timedelta(days=1))

    def test_06_cancel_and_reset(self):
        rec = self._movement()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_07_access_control(self):
        with self.assertRaises(Exception):
            self.env["returnable.package.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "partner_id": self.partner.id,
                    "package_type": "pallet",
                    "quantity": 1,
                    "movement_date": self.today,
                    "company_id": self.env.company.id,
                })
        rec = self._movement(name="RPL-ACC")
        rec.with_user(self.manager).read()

    def test_08_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "RPL B"})
        foreign = self.env["returnable.package.log"].create({
            "name": "RPL-FOREIGN",
            "partner_id": self.partner.id,
            "package_type": "pallet",
            "quantity": 1,
            "movement_date": self.today,
            "company_id": company_b.id,
        })
        visible = self.env["returnable.package.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
