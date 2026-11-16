# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGasCylinderLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env["res.partner"].create({"name": "Gas Supplier"})
        cls.manager = cls._user(
            "gcl-manager",
            ["gas_cylinder_log.group_gascylinderl_user"])
        cls.outsider = cls._user("gcl-outsider", ["base.group_user"])
        cls.today = fields.Date.context_today(cls.env.user)

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _cylinder(self, **vals):
        data = {
            "name": vals.pop("name", "GCL-TEST"),
            "cylinder_ref": "CYL-TEST",
            "gas_type": "oxygen",
            "capacity_l": 10.0,
            "supplier_id": self.supplier.id,
            "location": "Test Store",
            "last_test_date": self.today - timedelta(days=300),
            "next_test_date": self.today + timedelta(days=300),
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["gas.cylinder.log"].create(data)

    def test_01_create_cylinder(self):
        rec = self._cylinder()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.name)

    def test_02_use_empty_return(self):
        rec = self._cylinder()
        rec.action_use()
        self.assertEqual(rec.state, "in_use")
        rec.action_empty()
        self.assertEqual(rec.state, "empty")
        rec.action_return()
        self.assertEqual(rec.state, "returned")

    def test_03_invalid_transitions(self):
        rec = self._cylinder()
        with self.assertRaises(UserError):
            rec.action_empty()
        with self.assertRaises(UserError):
            rec.action_return()
        rec.action_use()
        with self.assertRaises(UserError):
            rec.action_use()
        rec.action_empty()
        with self.assertRaises(UserError):
            rec.action_empty()

    def test_04_constraints(self):
        with self.assertRaises(ValidationError):
            self._cylinder(capacity_l=-1.0)
        with self.assertRaises(ValidationError):
            self._cylinder(last_test_date=self.today,
                           next_test_date=self.today - timedelta(days=1))

    def test_05_cancel_and_reset(self):
        rec = self._cylinder()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["gas.cylinder.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "cylinder_ref": "NO",
                    "company_id": self.env.company.id,
                })
        rec = self._cylinder(name="GCL-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "GCL B"})
        foreign = self.env["gas.cylinder.log"].create({
            "name": "GCL-FOREIGN",
            "cylinder_ref": "CYL-B",
            "company_id": company_b.id,
        })
        visible = self.env["gas.cylinder.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
