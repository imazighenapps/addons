# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGSheetsSync(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conn = cls.env["gsheets.connection"].create({
            "name": "Sheet", "spreadsheet_id": "SID", "credential_ref": "cred",
        })
        cls.job = cls.env["gsheets.job"].create({
            "name": "Partners", "connection_id": cls.conn.id,
            "model_name": "res.partner", "field_names": "name,email",
        })

    def test_01_activate_requires_cred(self):
        c = self.env["gsheets.connection"].create({"name": "X", "spreadsheet_id": "S"})
        with self.assertRaises(UserError): c.action_activate()

    def test_02_run_requires_active(self):
        with self.assertRaises(UserError): self.job.action_run()

    def test_03_run_success(self):
        self.conn.action_activate()
        self.job.action_run()
        self.assertEqual(self.job.last_status, "ok")
        self.assertTrue(self.job.run_ids)

    def test_04_unknown_model_handled(self):
        self.conn.action_activate()
        self.job.model_name = "x.unknown.model"
        self.job.action_run()
        self.assertTrue(self.job.run_ids)

    def test_05_field_required(self):
        with self.assertRaises(ValidationError):
            self.job.write({"field_names": "  "})

    def test_06_multiple_runs(self):
        self.conn.action_activate()
        self.job.action_run(); self.job.action_run()
        self.assertEqual(len(self.job.run_ids), 2)

    def test_07_last_run_set(self):
        self.conn.action_activate(); self.job.action_run()
        self.assertTrue(self.job.last_run_at)

    def test_08_company_link(self):
        self.assertEqual(self.job.company_id, self.conn.company_id)
