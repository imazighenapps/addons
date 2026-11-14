# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPettyCashBox(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.box = cls.env["petty.cash.box"].create({
            "name": "Office Box",
            "opening_balance": 100.0,
            "company_id": cls.env.company.id,
        })
        cls.manager = cls._user(
            "pettycash-manager", ["petty_cash_box.group_pettycashbox_user"])
        cls.outsider = cls._user(
            "pettycash-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login,
            "login": login,
            field: [(6, 0, groups)],
        })

    def test_01_balance_computation(self):
        self.assertAlmostEqual(self.box.balance, 100.0)
        top = self.env["petty.cash.movement"].create({
            "box_id": self.box.id,
            "movement_type": "in",
            "amount": 50.0,
        })
        top.action_post()
        self.assertAlmostEqual(self.box.balance, 150.0)
        exp = self.env["petty.cash.movement"].create({
            "box_id": self.box.id,
            "movement_type": "out",
            "amount": 30.0,
        })
        exp.action_post()
        self.assertAlmostEqual(self.box.balance, 120.0)

    def test_02_count_difference(self):
        count = self.env["petty.cash.count"].create({
            "box_id": self.box.id,
            "counted_amount": 90.0,
        })
        self.assertAlmostEqual(count.expected_amount, 100.0)
        self.assertAlmostEqual(count.difference, -10.0)
        count.action_done()
        self.assertEqual(count.state, "done")

    def test_03_amount_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.env["petty.cash.movement"].create({
                "box_id": self.box.id,
                "movement_type": "out",
                "amount": -5.0,
            })

    def test_04_access_control(self):
        with self.assertRaises(Exception):
            self.env["petty.cash.box"].with_user(self.outsider).create({
                "name": "No Access Box",
                "company_id": self.env.company.id,
            })
        self.box.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Petty B"})
        foreign = self.env["petty.cash.box"].create({
            "name": "Foreign Box",
            "company_id": company_b.id,
        })
        visible = self.env["petty.cash.box"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
