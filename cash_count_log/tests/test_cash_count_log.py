# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCashCountLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "ccl-manager",
            ["cash_count_log.group_cashcountlog_user"])
        cls.outsider = cls._user("ccl-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _count(self, **vals):
        data = {
            "name": vals.pop("name", "CCL-TEST"),
            "count_date": fields.Date.context_today(self.env.user),
            "expected_amount": 100.0,
            "counted_amount": 95.0,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["cash.count.log"].create(data)

    def test_01_create_count(self):
        rec = self._count()
        self.assertEqual(rec.state, "draft")
        self.assertAlmostEqual(rec.difference, -5.0)

    def test_02_submit_validate_flow(self):
        rec = self._count()
        rec.action_submit()
        self.assertEqual(rec.state, "submitted")
        rec.action_validate()
        self.assertEqual(rec.state, "validated")
        self.assertTrue(rec.reviewer_id)

    def test_03_reset_draft(self):
        rec = self._count()
        rec.action_submit()
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._count()
        with self.assertRaises(UserError):
            rec.action_validate()
        rec.action_submit()
        rec.action_validate()
        with self.assertRaises(UserError):
            rec.action_submit()

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["cash.count.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "company_id": self.env.company.id,
                })
        rec = self._count(name="CCL-ACC")
        rec.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "CCL B"})
        foreign = self.env["cash.count.log"].create({
            "name": "CCL-FOREIGN",
            "company_id": company_b.id,
        })
        visible = self.env["cash.count.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
