# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFireExtinguisherLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspector = cls.env["hr.employee"].create({"name": "Fire Inspector"})
        cls.manager = cls._user(
            "fel-manager",
            ["fire_extinguisher_log.group_fireextingui_user"])
        cls.outsider = cls._user("fel-outsider", ["base.group_user"])
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
            "name": vals.pop("name", "FEL-TEST"),
            "extinguisher_ref": "EXT-TEST",
            "location": "Test Site",
            "extinguisher_type": "powder",
            "last_inspection_date": self.today,
            "next_inspection_date": self.today + timedelta(days=365),
            "inspector_id": self.inspector.id,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["fire.extinguisher.log"].create(data)

    def test_01_create_inspection(self):
        rec = self._record()
        self.assertEqual(rec.state, "draft")
        self.assertTrue(rec.name)

    def test_02_validate_and_overdue(self):
        rec = self._record()
        rec.action_validate()
        self.assertEqual(rec.state, "validated")
        rec.action_mark_overdue()
        self.assertEqual(rec.state, "overdue")

    def test_03_validation_requires_checks(self):
        rec = self._record(pressure_ok=False)
        with self.assertRaises(UserError):
            rec.action_validate()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._record()
        with self.assertRaises(UserError):
            rec.action_mark_overdue()
        rec.action_validate()
        with self.assertRaises(UserError):
            rec.action_validate()

    def test_05_constraints(self):
        with self.assertRaises(ValidationError):
            self._record(capacity_kg=-1.0)
        with self.assertRaises(ValidationError):
            self._record(
                next_inspection_date=self.today - timedelta(days=1))

    def test_06_cancel_and_reset(self):
        rec = self._record()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_07_access_control(self):
        with self.assertRaises(Exception):
            self.env["fire.extinguisher.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "extinguisher_ref": "NO",
                    "location": "No",
                    "company_id": self.env.company.id,
                })
        rec = self._record(name="FEL-ACC")
        rec.with_user(self.manager).read()

    def test_08_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "FEL B"})
        foreign = self.env["fire.extinguisher.log"].create({
            "name": "FEL-FOREIGN",
            "extinguisher_ref": "EXT-B",
            "location": "Foreign",
            "last_inspection_date": self.today,
            "next_inspection_date": self.today + timedelta(days=365),
            "company_id": company_b.id,
        })
        visible = self.env["fire.extinguisher.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
