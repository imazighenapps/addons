# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDunningLetterAutomation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Dunning Customer", "is_company": True,
            "customer_rank": 1,
        })
        cls.product = cls.env["product.product"].create({
            "name": "Dunning Service", "type": "service",
            "list_price": 100.0,
        })
        cls.level = cls.env["dunning.letter.level"].create({
            "name": "First reminder", "sequence": 10, "days_after_due": 7,
            "subject": "Reminder", "body": "Please pay.",
        })
        cls.manager = cls._user(
            "dun-manager", ["dunning_letter_automation.group_dunninglette_user"])
        cls.outsider = cls._user("dun-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _invoice(self, due, post=True):
        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "invoice_date": date(2099, 1, 1),
            "invoice_date_due": due,
            "invoice_line_ids": [(0, 0, {
                "product_id": self.product.id,
                "quantity": 1.0,
                "price_unit": 100.0,
                "tax_ids": [(5, 0, 0)],
            })],
        })
        if post:
            move.action_post()
        return move

    def _generate(self, as_of=None, levels=None, moves=None):
        wizard = self.env["dunning.generate"].create({
            "as_of_date": as_of or date(2099, 3, 1),
            "level_ids": [(6, 0, (levels or self.level).ids)],
        })
        wizard.action_generate()
        domain = [("level_id", "in", (levels or self.level).ids),
                  ("partner_id", "=", self.partner.id)]
        if moves:
            domain.append(("move_id", "in", moves.ids))
        return self.env["dunning.letter"].search(domain)

    def test_01_overdue_invoice_gets_a_letter(self):
        move = self._invoice(date(2099, 1, 20))
        letters = self._generate(date(2099, 3, 1))
        self.assertEqual(len(letters), 1)
        self.assertEqual(letters.move_id, move)
        self.assertEqual(letters.amount_residual, move.amount_residual)
        self.assertEqual(letters.due_date, date(2099, 1, 20))

    def test_02_recent_invoice_is_not_dunned(self):
        self._invoice(date(2099, 2, 27))
        letters = self._generate(date(2099, 3, 1))
        self.assertFalse(letters)

    def test_03_draft_invoice_is_ignored(self):
        self._invoice(date(2099, 1, 10), post=False)
        self.assertFalse(self._generate(date(2099, 3, 1)))

    def test_04_no_duplicate_open_letter(self):
        self._invoice(date(2099, 1, 20))
        first = self._generate(date(2099, 3, 1))
        second = self._generate(date(2099, 3, 1))
        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)

    def test_05_send_then_pay(self):
        self._invoice(date(2099, 1, 20))
        letter = self._generate(date(2099, 3, 1))
        letter.action_send()
        self.assertEqual(letter.state, "sent")
        self.assertTrue(letter.sent_date)
        letter.action_mark_paid()
        self.assertEqual(letter.state, "paid")
        with self.assertRaises(UserError):
            letter.action_cancel()

    def test_06_cancel_and_reset(self):
        letter = self.env["dunning.letter"].create({
            "partner_id": self.partner.id,
            "level_id": self.level.id,
        })
        letter.action_cancel()
        self.assertEqual(letter.state, "cancelled")
        letter.action_reset_draft()
        self.assertEqual(letter.state, "draft")

    def test_07_negative_delay_is_refused(self):
        with self.assertRaises(ValidationError):
            self.env["dunning.letter.level"].create({
                "name": "Broken", "days_after_due": -3,
            })

    def test_08_access_control(self):
        with self.assertRaises(Exception):
            self.env["dunning.letter"].with_user(self.outsider).create({
                "partner_id": self.partner.id,
                "level_id": self.level.id,
            })
        letter = self.env["dunning.letter"].create({
            "partner_id": self.partner.id,
            "level_id": self.level.id,
        })
        letter.with_user(self.manager).read()

    def test_09_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Dunning B"})
        foreign = self.env["dunning.letter"].create({
            "partner_id": self.partner.id,
            "level_id": self.level.id,
            "company_id": company_b.id,
        })
        visible = self.env["dunning.letter"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
