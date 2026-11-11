# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestKittingDeskEntry(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.rec = cls.env["kitting_desk.entry"].create({
            "name": "Test KitDesk",
            "partner_id": cls.partner.id,
        })

    def test_01_create(self):
        self.assertTrue(self.rec.id)
        self.assertEqual(self.rec.state, "draft")

    def test_02_confirm(self):
        self.rec.action_confirm()
        self.assertEqual(self.rec.state, "confirmed")

    def test_03_done(self):
        self.rec.action_confirm()
        self.rec.action_done()
        self.assertEqual(self.rec.state, "done")

    def test_04_cancel_reset(self):
        self.rec.action_confirm()
        self.rec.action_cancel()
        self.assertEqual(self.rec.state, "cancelled")
        self.rec.action_draft()
        self.assertEqual(self.rec.state, "draft")

    def test_05_line(self):
        line = self.env["kitting_desk.item"].create({
            "entry_id": self.rec.id, "name": "L1", "quantity": 2, "price": 10,
        })
        self.assertEqual(line.subtotal, 20)
        self.assertEqual(self.rec.line_count, 1)

    def test_06_date_constraint(self):
        with self.assertRaises(ValidationError):
            self.rec.write({"date_start": "2026-01-10", "date_end": "2026-01-01"})

    def test_07_wrong_state_confirm(self):
        self.rec.action_confirm()
        with self.assertRaises(UserError):
            self.rec.action_confirm()

    def test_08_done_no_cancel(self):
        self.rec.action_confirm()
        self.rec.action_done()
        with self.assertRaises(UserError):
            self.rec.action_cancel()
