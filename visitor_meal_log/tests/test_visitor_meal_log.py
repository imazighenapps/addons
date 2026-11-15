# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVisitorMealLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Host Employee"})
        cls.manager = cls._user(
            "vml-manager",
            ["visitor_meal_log.group_visitormeall_user"])
        cls.outsider = cls._user("vml-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _meal(self, **vals):
        data = {
            "name": vals.pop("name", "VML-TEST"),
            "host_id": self.employee.id,
            "meal_date": fields.Date.context_today(self.env.user),
            "meal_count": 3,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["visitor.meal.log"].create(data)

    def test_01_create_meal(self):
        rec = self._meal()
        self.assertEqual(rec.state, "draft")

    def test_02_request_serve_flow(self):
        rec = self._meal()
        rec.action_request()
        self.assertEqual(rec.state, "requested")
        rec.action_serve()
        self.assertEqual(rec.state, "served")

    def test_03_cancel_and_reset(self):
        rec = self._meal()
        rec.action_cancel()
        self.assertEqual(rec.state, "cancelled")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._meal()
        with self.assertRaises(UserError):
            rec.action_serve()
        rec.action_request()
        rec.action_serve()
        with self.assertRaises(UserError):
            rec.action_cancel()

    def test_05_meal_count_validation(self):
        with self.assertRaises(ValidationError):
            self._meal(meal_count=0)

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["visitor.meal.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "meal_count": 1,
                    "company_id": self.env.company.id,
                })
        rec = self._meal(name="VML-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "VML B"})
        foreign = self.env["visitor.meal.log"].create({
            "name": "VML-FOREIGN",
            "meal_count": 2,
            "company_id": company_b.id,
        })
        visible = self.env["visitor.meal.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
