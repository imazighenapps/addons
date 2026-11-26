# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo import fields


class TestFinancialReport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.report = cls.env["fr.report"].create({
            "name": "Test P&L",
            "report_type": "pl",
            "company_id": cls.company.id,
        })
        cls.env["fr.report.line"].create({
            "report_id": cls.report.id,
            "name": "Income",
            "line_type": "line",
            "internal_group": "income",
            "sign": "1",
            "sequence": 10,
        })
        cls.env["fr.report.line"].create({
            "report_id": cls.report.id,
            "name": "Expenses",
            "line_type": "line",
            "internal_group": "expense",
            "sign": "-1",
            "sequence": 20,
        })

    def test_wizard_computes_rows(self):
        today = fields.Date.today()
        wizard = self.env["fr.report.wizard"].create({
            "report_id": self.report.id,
            "company_id": self.company.id,
            "date_from": today.replace(month=1, day=1),
            "date_to": today,
        })
        data = wizard._get_report_data()
        self.assertEqual(data["report"]["name"], "Test P&L")
        self.assertEqual(len(data["rows"]), 2)
        self.assertIn("amount", data["rows"][0])

    def test_csv_export(self):
        today = fields.Date.today()
        wizard = self.env["fr.report.wizard"].create({
            "report_id": self.report.id,
            "company_id": self.company.id,
            "date_from": today.replace(month=1, day=1),
            "date_to": today,
        })
        action = wizard.action_export_csv()
        self.assertEqual(action["type"], "ir.actions.act_url")
