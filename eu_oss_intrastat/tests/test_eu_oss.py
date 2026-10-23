# -*- coding: utf-8 -*-
import base64

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

PERIOD = fields.Date.today().strftime("%Y-%m")


@tagged("post_install", "-at_install")
class TestEuOss(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country = cls.env.ref("base.be")
        cls.oss_th = cls.env.ref("eu_oss_intrastat.threshold_oss")
        cls.ioss_th = cls.env.ref("eu_oss_intrastat.threshold_ioss")
        cls.customer = cls.env["res.partner"].create({
            "name": "Demo BE Customer", "is_company": True,
            "country_id": cls.country.id})
        cls.service = cls.env["product.product"].create({
            "name": "Consulting", "type": "service"})
        # Accounts live in setUpClass so they survive every test rollback.
        cls.income = cls.env["account.account"].create({
            "name": "Test Income OSS", "code": "707EOSS",
            "account_type": "income"})
        cls.receivable = cls.env["account.account"].create({
            "name": "Test Receivable OSS", "code": "411EOSS",
            "account_type": "asset_receivable"})
        cls.customer.property_account_receivable_id = cls.receivable.id
        cls.sale_journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1)
        # Other modules (FR e-invoicing) may hard-block posting customer
        # invoices; that is out of scope for these tests.
        cls.env["ir.config_parameter"].sudo().set_param(
            "fr_einvoicing_pack.block_noncompliant", "False")

    def _invoice(self, price=500.0):
        return self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.customer.id,
            "journal_id": self.sale_journal.id,
            "fiscal_position_id": False,
            "invoice_date": fields.Date.today(),
            "invoice_line_ids": [(0, 0, {
                "name": "Service", "quantity": 1.0, "price_unit": price,
            })],
        })

    def _counter(self, oss=0.0, ioss=0.0):
        return self.env["oss.country.counter"].create({
            "country_id": self.country.id,
            "oss_amount": oss, "ioss_amount": ioss})

    def test_01_seed_thresholds(self):
        self.assertEqual(self.oss_th.limit, 10000.0)
        self.assertEqual(self.ioss_th.limit, 150.0)

    def test_02_state_clear(self):
        rec = self._counter(oss=1000.0, ioss=10.0)
        self.assertEqual(rec.state, "clear")
        self.assertAlmostEqual(rec.oss_ratio, 0.1, places=3)

    def test_03_state_near(self):
        rec = self._counter(oss=8500.0, ioss=0.0)
        self.assertEqual(rec.state, "near")
        self.assertAlmostEqual(rec.oss_ratio, 0.85, places=3)

    def test_04_state_oss_due(self):
        rec = self._counter(oss=12000.0, ioss=0.0)
        self.assertEqual(rec.state, "oss_due")

    def test_05_state_ioss_due(self):
        rec = self._counter(oss=0.0, ioss=200.0)
        self.assertEqual(rec.state, "ioss_due")

    def test_06_intrastat_line_flow(self):
        move = self._invoice(500.0)
        move.action_post()
        self.env["intrastat.line"]._cron_prepare()
        line = self.env["intrastat.line"].search([("move_id", "=", move.id)])
        self.assertTrue(line)
        self.assertEqual(line.country_code, "BE")
        self.assertEqual(line.state, "draft")
        line.action_mark_ready()
        self.assertEqual(line.state, "ready")
        line.action_mark_declared()
        self.assertEqual(line.state, "declared")

    def test_07_declare_without_country_blocked(self):
        move = self._invoice(100.0)
        line = self.env["intrastat.line"].create({"move_id": move.id})
        with self.assertRaises(UserError):
            line.action_mark_declared()

    def test_08_export_csv(self):
        move = self._invoice(250.0)
        line = self.env["intrastat.line"].create({
            "move_id": move.id,
            "partner_country_id": self.country.id,
            "period": PERIOD, "state": "ready"})
        wizard = self.env["intrastat.export"].create({
            "period": PERIOD, "direction": "dispatch",
            "only_ready": True, "line_ids": [(6, 0, line.ids)]})
        wizard.action_export()
        self.assertEqual(wizard.state, "done")
        self.assertTrue(wizard.filename.endswith(".csv"))
        payload = base64.b64decode(wizard.file_data).decode("utf-8")
        self.assertIn("period;direction", payload)
        self.assertIn("BE", payload)
