# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEmployeeTrainingRecord(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Train Test Employee"})
        cls.ttype = cls.env["employee.training.type"].create({
            "name": "Safety", "validity_days": 365})
        cls.manager = cls._user(
            "training-manager", ["employee_training_record.group_employeetrai_user"])
        cls.outsider = cls._user(
            "training-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def test_01_create_and_status_valid(self):
        today = fields.Date.context_today(self.env.user)
        rec = self.env["employee.training.record"].create({
            "name": "Safety Basics",
            "employee_id": self.employee.id,
            "type_id": self.ttype.id,
            "date_done": today,
            "date_expiry": today + timedelta(days=200),
            "company_id": self.env.company.id,
        })
        self.assertEqual(rec.state, "done")
        self.assertEqual(rec.status, "valid")

    def test_02_expired_status(self):
        today = fields.Date.context_today(self.env.user)
        rec = self.env["employee.training.record"].create({
            "name": "Old Training",
            "employee_id": self.employee.id,
            "date_done": today - timedelta(days=400),
            "date_expiry": today - timedelta(days=10),
            "company_id": self.env.company.id,
        })
        self.assertEqual(rec.status, "expired")

    def test_03_expiring_status(self):
        today = fields.Date.context_today(self.env.user)
        rec = self.env["employee.training.record"].create({
            "name": "Soon Expiring",
            "employee_id": self.employee.id,
            "date_done": today - timedelta(days=340),
            "date_expiry": today + timedelta(days=10),
            "company_id": self.env.company.id,
        })
        self.assertEqual(rec.status, "expiring")

    def test_04_date_check(self):
        today = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self.env["employee.training.record"].create({
                "name": "Bad Dates",
                "employee_id": self.employee.id,
                "date_done": today,
                "date_expiry": today - timedelta(days=1),
                "company_id": self.env.company.id,
            })

    def test_05_access_control(self):
        today = fields.Date.context_today(self.env.user)
        rec = self.env["employee.training.record"].create({
            "name": "Access Test",
            "employee_id": self.employee.id,
            "date_done": today,
            "company_id": self.env.company.id,
        })
        with self.assertRaises(Exception):
            self.env["employee.training.record"].with_user(self.outsider).create({
                "name": "No",
                "employee_id": self.employee.id,
                "date_done": today,
                "company_id": self.env.company.id,
            })
        rec.with_user(self.manager).read()

    def test_06_company_isolation(self):
        today = fields.Date.context_today(self.env.user)
        company_b = self.env["res.company"].create({"name": "Train B"})
        emp_b = self.env["hr.employee"].create({
            "name": "Emp B", "company_id": company_b.id})
        foreign = self.env["employee.training.record"].create({
            "name": "Foreign",
            "employee_id": emp_b.id,
            "date_done": today,
            "company_id": company_b.id,
        })
        visible = self.env["employee.training.record"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
