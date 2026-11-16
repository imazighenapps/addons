# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPettyExpenseLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "pel-manager",
            ["petty_expense_log.group_pettyexpense_user"])
        cls.outsider = cls._user("pel-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _expense(self, **vals):
        data = {
            "name": vals.pop("name", "PEL-TEST"),
            "expense_date": fields.Date.context_today(self.env.user),
            "amount": 15.0,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["petty.expense.log"].create(data)

    def test_01_create_expense(self):
        rec = self._expense()
        self.assertEqual(rec.state, "draft")

    def test_02_approve_reimburse_flow(self):
        rec = self._expense()
        rec.action_submit()
        self.assertEqual(rec.state, "submitted")
        rec.action_approve()
        self.assertEqual(rec.state, "approved")
        rec.action_reimburse()
        self.assertEqual(rec.state, "reimbursed")

    def test_03_reject_and_reset(self):
        rec = self._expense()
        rec.action_submit()
        rec.action_reject()
        self.assertEqual(rec.state, "rejected")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._expense()
        with self.assertRaises(UserError):
            rec.action_approve()
        rec.action_submit()
        with self.assertRaises(UserError):
            rec.action_reimburse()

    def test_05_amount_validation(self):
        with self.assertRaises(ValidationError):
            self._expense(amount=0)

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["petty.expense.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "amount": 5.0,
                    "company_id": self.env.company.id,
                })
        rec = self._expense(name="PEL-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "PEL B"})
        foreign = self.env["petty.expense.log"].create({
            "name": "PEL-FOREIGN",
            "amount": 10.0,
            "company_id": company_b.id,
        })
        visible = self.env["petty.expense.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
