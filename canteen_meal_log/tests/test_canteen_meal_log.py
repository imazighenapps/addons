# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCanteenMealLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "canteen-manager", ["canteen_meal_log.group_canteenmeall_user"])
        cls.outsider = cls._user(
            "canteen-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _log(self):
        return self.env["canteen.meal.log"].create({
            "meal_type": "lunch",
            "headcount": 50,
            "cost": 200.0,
            "company_id": self.env.company.id,
        })

    def test_01_confirm(self):
        l = self._log()
        l.action_confirm()
        self.assertEqual(l.state, "confirmed")
        l.action_reset()
        self.assertEqual(l.state, "draft")

    def test_02_state_guards(self):
        l = self._log()
        l.action_confirm()
        with self.assertRaises(UserError):
            l.action_confirm()

    def test_03_validation(self):
        with self.assertRaises(ValidationError):
            self.env["canteen.meal.log"].create({
                "meal_type": "lunch",
                "headcount": -1,
                "company_id": self.env.company.id,
            })

    def test_04_access_control(self):
        l = self._log()
        with self.assertRaises(Exception):
            self.env["canteen.meal.log"].with_user(self.outsider).create({
                "meal_type": "lunch",
                "headcount": 1,
                "company_id": self.env.company.id,
            })
        l.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Can B"})
        foreign = self.env["canteen.meal.log"].create({
            "meal_type": "lunch",
            "headcount": 10,
            "company_id": company_b.id,
        })
        visible = self.env["canteen.meal.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
