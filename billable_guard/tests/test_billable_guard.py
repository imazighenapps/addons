# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBillableGuard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Billable Test Customer", "is_company": True})
        cls.product = cls.env["product.product"].create({
            "name": "Billable Test Service", "type": "service",
            "list_price": 100.0, "invoice_policy": "delivery"})
        cls.project = cls.env["project.project"].create({
            "name": "Billable Test Project", "partner_id": cls.partner.id})
        cls.task = cls.env["project.task"].create({
            "name": "Billable Test Task", "project_id": cls.project.id})
        cls.employee = cls.env["hr.employee"].create({
            "name": "Billable Test Employee"})
        cls.order = cls.env["sale.order"].create({
            "partner_id": cls.partner.id,
            "order_line": [(0, 0, {
                "product_id": cls.product.id,
                "product_uom_qty": 10.0,
                "price_unit": 100.0,
            })],
        })
        cls.order.action_confirm()
        cls.sale_line = cls.order.order_line[:1]

    def _timesheet(self, hours, task=None, invoice=None):
        line = self.env["account.analytic.line"].create({
            "name": "Billable work",
            "project_id": self.project.id,
            "task_id": (task or self.task).id,
            "employee_id": self.employee.id,
            "unit_amount": hours,
            "date": date(2099, 2, 10),
        })
        if invoice:
            # 20.0 renamed timesheet_invoice_id to reinvoice_move_id.
            field = "reinvoice_move_id" \
                if "reinvoice_move_id" in line._fields \
                else "timesheet_invoice_id"
            line.write({field: invoice.id})
        return line

    def _scan(self, min_hours=0.5):
        wizard = self.env["billable.gap.scan"].create({
            "date_from": date(2099, 2, 1),
            "date_to": date(2099, 2, 28),
            "min_hours": min_hours,
        })
        wizard.action_run()
        return self.env["billable.gap"].search([
            ("project_id", "=", self.project.id),
            ("date_from", "=", date(2099, 2, 1)),
            ("state", "=", "open"),
        ])

    def test_01_scan_creates_a_gap(self):
        self._timesheet(6.0)
        gaps = self._scan()
        self.assertEqual(len(gaps), 1)
        self.assertAlmostEqual(gaps.hours_logged, 6.0, places=2)
        self.assertAlmostEqual(gaps.hours_gap, 6.0, places=2)

    def test_02_hours_below_threshold_are_ignored(self):
        self._timesheet(0.2)
        self.assertFalse(self._scan(min_hours=0.5))

    def test_03_second_scan_does_not_duplicate(self):
        self._timesheet(4.0)
        self._scan()
        self._scan()
        self.assertEqual(len(self._scan()), 1)

    def test_04_invoiced_timesheets_are_excluded(self):
        move = self.env["account.move"].create({
            "move_type": "out_invoice", "partner_id": self.partner.id})
        self._timesheet(5.0, invoice=move)
        self.assertFalse(self._scan())

    def test_05_ignore_and_reopen(self):
        self._timesheet(3.0)
        gap = self._scan()
        self.assertTrue(gap.action_ignore())
        self.assertEqual(gap.state, "ignored")
        self.assertFalse(self._scan())
        self.assertTrue(gap.action_reopen())
        self.assertEqual(gap.state, "open")

    def test_06_project_risk(self):
        self._timesheet(3.0)
        other_task = self.env["project.task"].create({
            "name": "Billable Second Task", "project_id": self.project.id})
        self._timesheet(2.0, task=other_task)
        self._scan()
        self.project.invalidate_recordset()
        self.assertEqual(self.project.billable_gap_count, 2)
        self.assertEqual(self.project.billable_risk, "high")

    def test_07_amount_at_risk_and_invoice_action(self):
        self._timesheet(6.0)
        gap = self._scan()
        gap.sale_line_id = self.sale_line.id
        gap.hours_invoiced = 2.0
        gap.invalidate_recordset()
        self.assertAlmostEqual(gap.hours_gap, 4.0, places=2)
        self.assertAlmostEqual(gap.amount_at_risk, 400.0, places=2)
        action = gap.action_create_invoice()
        self.assertEqual(action["res_model"], "sale.advance.payment.inv")
        gap.sale_line_id = False
        self.assertFalse(gap.action_create_invoice())

    def test_08_company_isolation(self):
        other = self.env["res.company"].create({
            "name": "Billable Other Company"})
        self._timesheet(4.0)
        gaps = self._scan()
        self.assertEqual(gaps.company_id, self.env.company)
        self.assertNotEqual(gaps.company_id, other)
