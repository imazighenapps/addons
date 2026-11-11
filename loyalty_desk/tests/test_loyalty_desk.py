# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPointsBank(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "PointsBank Other Company"})

    def _account(self, **values):
        defaults = {
            "name": "PointsBank Account",
            "partner_name": "PointsBank Customer A",
        }
        defaults.update(values)
        return self.env["loyalty.account"].create(defaults)

    def _move(self, account, **values):
        defaults = {
            "name": "PointsBank Move",
            "account_id": account.id,
            "move_type": "earn",
            "points": 100,
            "move_date": date(2026, 4, 10),
            "reference": "PB-INV-001",
        }
        defaults.update(values)
        return self.env["loyalty.move"].create(defaults)

    def test_01_account_defaults(self):
        account = self._account()
        self.assertEqual(account.state, "active")
        self.assertEqual(account.company_id, self.env.company)
        self.assertEqual(account.balance_points, 0)
        self.assertEqual(account.move_count, 0)

    def test_02_earn_and_balance(self):
        account = self._account()
        move = self._move(account, points=120)
        self.assertTrue(move.action_post())
        self.assertEqual(move.state, "posted")
        account.invalidate_recordset()
        self.assertEqual(account.points_earned, 120)
        self.assertEqual(account.balance_points, 120)
        self.assertEqual(account.move_count, 1)

    def test_03_redeem_updates_balance(self):
        account = self._account(partner_name="PointsBank Customer B")
        earn = self._move(account, points=80, move_date=date(2026, 4, 11))
        earn.action_post()
        redeem = self._move(account, move_type="redeem", points=30,
                            move_date=date(2026, 4, 12), name="PointsBank Redeem")
        redeem.action_post()
        account.invalidate_recordset()
        self.assertEqual(account.points_earned, 80)
        self.assertEqual(account.points_redeemed, 30)
        self.assertEqual(account.balance_points, 50)

    def test_04_redeem_over_balance_is_refused(self):
        account = self._account(partner_name="PointsBank Customer C")
        earn = self._move(account, points=20, move_date=date(2026, 5, 1))
        earn.action_post()
        redeem = self._move(account, move_type="redeem", points=25,
                            move_date=date(2026, 5, 2), name="PointsBank Overdraw")
        with self.assertRaises(UserError):
            redeem.action_post()

    def test_05_points_must_be_positive(self):
        account = self._account(partner_name="PointsBank Customer D")
        with self.assertRaises(ValidationError):
            self._move(account, points=0)
        with self.assertRaises(ValidationError):
            self._move(account, points=-5)

    def test_06_suspend_and_activate(self):
        account = self._account(partner_name="PointsBank Customer E")
        self.assertTrue(account.action_suspend())
        self.assertEqual(account.state, "suspended")
        with self.assertRaises(UserError):
            account.action_suspend()
        self.assertTrue(account.action_activate())
        self.assertEqual(account.state, "active")
        with self.assertRaises(UserError):
            account.action_activate()

    def test_07_cannot_post_on_suspended_account(self):
        account = self._account(partner_name="PointsBank Customer F")
        move = self._move(account, points=40, move_date=date(2026, 6, 1))
        account.action_suspend()
        with self.assertRaises(UserError):
            move.action_post()

    def test_08_post_only_once(self):
        account = self._account(partner_name="PointsBank Customer G")
        move = self._move(account, points=15, move_date=date(2026, 6, 15))
        move.action_post()
        with self.assertRaises(UserError):
            move.action_post()

    def test_09_company_isolation(self):
        foreign = self.env["loyalty.account"].with_company(
            self.other_company).sudo().create({
            "name": "PointsBank Foreign",
            "partner_name": "PointsBank Foreign Customer",
            "company_id": self.other_company.id,
        })
        local = self._account(partner_name="PointsBank Local Customer")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
