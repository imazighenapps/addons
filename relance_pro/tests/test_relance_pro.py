# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRelancePro(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Dunning Test Customer", "is_company": True,
            "email": "dunning@example.com"})
        cls.product = cls.env["product.product"].create({
            "name": "Dunning Test Product", "type": "service",
            "list_price": 100.0})
        cls.template = cls.env["mail.template"].create({
            "name": "Dunning Test Template",
            "model_id": cls.env["ir.model"].search(
                [("model", "=", "dunning.line")], limit=1).id,
            "subject": "Invoice overdue",
            "body_html": "<p>Your invoice is overdue.</p>",
        })

    def _invoice(self, due):
        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "invoice_date": date(2098, 12, 1),
            "invoice_date_due": due,
            "invoice_line_ids": [(0, 0, {
                "product_id": self.product.id,
                "quantity": 1.0,
                "price_unit": 100.0,
            })],
        })
        move.action_post()
        return move

    def _level(self, offset, fee=0.0, name=None):
        return self.env["dunning.level"].create({
            "name": name or "Level %s" % offset,
            "day_offset": offset,
            "template_id": self.template.id,
            "fee_amount": fee,
        })

    def _run(self, ref=date(2099, 2, 15), dry_run=False, partner_ids=None):
        values = {
            "date_ref": ref,
            "dry_run": dry_run,
            "partner_ids": [(6, 0, partner_ids or [])],
        }
        wizard = self.env["dunning.run.wizard"].create(values)
        wizard.action_run()

    def _lines(self, move):
        return self.env["dunning.line"].search([("move_id", "=", move.id)])

    def test_01_overdue_invoice_is_chased(self):
        self._level(7)
        move = self._invoice(date(2099, 1, 5))
        self._run()
        self.assertEqual(len(self._lines(move)), 1)
        self.assertEqual(self._lines(move).state, "sent")

    def test_02_not_due_invoice_is_ignored(self):
        self._level(7)
        move = self._invoice(date(2099, 3, 5))
        self._run()
        self.assertFalse(self._lines(move))

    def test_03_highest_level_only(self):
        self._level(7)
        self._level(30)
        move = self._invoice(date(2099, 1, 5))
        self._run()
        lines = self._lines(move)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines.level_id.day_offset, 30)

    def test_04_no_duplicate_on_second_run(self):
        self._level(7)
        move = self._invoice(date(2099, 1, 5))
        self._run()
        self._run()
        self.assertEqual(len(self._lines(move)), 1)
        with self.assertRaises(Exception):
            self.env["dunning.line"].create({
                "partner_id": self.partner.id,
                "move_id": move.id,
                "level_id": self._lines(move).level_id.id,
            })

    def test_05_paused_customer_is_skipped(self):
        self._level(7)
        self.partner.dunning_paused = True
        move = self._invoice(date(2099, 1, 5))
        self._run()
        self.assertFalse(self._lines(move))

    def test_06_late_fee_is_recorded(self):
        self._level(7, fee=15.0)
        move = self._invoice(date(2099, 1, 5))
        self._run()
        self.assertAlmostEqual(self._lines(move).fee_amount, 15.0, places=2)

    def test_07_dry_run_does_not_send(self):
        self._level(7)
        move = self._invoice(date(2099, 1, 5))
        self._run(dry_run=True)
        line = self._lines(move)
        self.assertEqual(line.state, "draft")
        self.assertFalse(line.sent_date)

    def test_08_company_isolation(self):
        other = self.env["res.company"].create({
            "name": "Dunning Other Company"})
        self._level(7)
        move = self._invoice(date(2099, 1, 5))
        self._run()
        lines = self._lines(move)
        self.assertEqual(lines.company_id, self.env.company)
        # A level of another company never joins the ladder of this one.
        foreign = self.env["dunning.level"].create({
            "name": "Other Level",
            "company_id": other.id,
            "day_offset": 60,
            "template_id": self.template.id,
        })
        self.assertNotIn(foreign, lines.level_id)
        self.assertNotEqual(lines.company_id, foreign.company_id)
