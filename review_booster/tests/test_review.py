# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReview(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.campaign = cls.env["review.campaign"].create({
            "name": "Post-delivery", "google_url": "https://g.page/demo",
            "trigger": "delivery", "delay_days": 0,
        })
        cls.invoice_campaign = cls.env["review.campaign"].create({
            "name": "Post-invoice", "google_url": "https://g.page/demo",
            "trigger": "invoice", "delay_days": 0,
        })
        cls.partner = cls.env["res.partner"].create({
            "name": "Happy Customer", "review_optin": True,
            "review_optin_proof": "Checkbox on order form",
        })
        # Other modules (FR e-invoicing) may hard-block posting customer
        # invoices; that is out of scope for these tests.
        cls.env["ir.config_parameter"].sudo().set_param(
            "fr_einvoicing_pack.block_noncompliant", "False")

    def _request(self, partner=None, campaign=None):
        return self.env["review.request"].create({
            "campaign_id": (campaign or self.campaign).id,
            "partner_id": (partner or self.partner).id})

    def test_01_token_unique(self):
        r1 = self._request()
        r2 = self._request()
        self.assertNotEqual(r1.token, r2.token)
        self.assertTrue(r1.name.startswith("REV-"))
        self.assertEqual(r1.state, "pending")

    def test_02_no_optin_no_send(self):
        self.partner.review_optin = False
        req = self._request()
        req.action_send()
        self.assertEqual(req.state, "optout")

    def test_03_send_and_click(self):
        req = self._request()
        req.action_send()
        self.assertEqual(req.state, "sent")
        self.assertTrue(req.sent_on)
        self.assertIn("/r/", req.review_link())
        req.action_mark_reviewed()
        self.assertEqual(req.state, "reviewed")

    def test_04_optout_propagates(self):
        req = self._request()
        req.action_optout()
        self.assertFalse(req.partner_id.review_optin)
        self.assertEqual(req.state, "optout")

    def test_05_invoice_creates_request(self):
        journal = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1)
        move = self.env["account.move"].create({
            "move_type": "out_invoice", "partner_id": self.partner.id,
            "journal_id": journal.id,
            "fiscal_position_id": False,
            "invoice_date": fields.Date.today(),
            "invoice_line_ids": [(0, 0, {
                "name": "Service", "quantity": 1.0, "price_unit": 50.0})],
        })
        move.action_post()
        reqs = self.env["review.request"].search([("move_id", "=", move.id)])
        self.assertEqual(len(reqs), 1)
        # a second post must not create a duplicate
        reqs.action_mark_reviewed()
        move.button_draft()
        move.action_post()
        self.assertEqual(
            self.env["review.request"].search_count([("move_id", "=", move.id)]), 1)

    def test_06_cron_sends_due(self):
        req = self._request()
        req.send_on = fields.Date.today()
        self.env["review.request"]._cron_send_due()
        self.assertEqual(req.state, "sent")