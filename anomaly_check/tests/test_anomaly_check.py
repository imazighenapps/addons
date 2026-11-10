# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAnomalyCheck(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "AnomalyCheck Other Company"})
        cls.rule = cls.env["anomaly.rule"].create({
            "name": "AnomalyCheck Qty Rule",
            "rule_type": "quantity",
            "severity": "high",
            "tolerance": 5.0,
        })

    def _flag(self, **values):
        defaults = {
            "name": "AnomalyCheck Flag",
            "rule_id": self.rule.id,
            "document_ref": "BILL-AC-2026-001",
            "partner_name": "ACME Supplies",
            "quantity": 2.0,
            "tax_amount": 20.0,
            "total_amount": 120.0,
            "flag_date": "2026-03-15",
        }
        defaults.update(values)
        return self.env["anomaly.flag"].create(defaults)

    def test_01_flag_defaults(self):
        flag = self._flag()
        self.assertEqual(flag.state, "new")
        self.assertEqual(flag.company_id, self.env.company)
        self.assertEqual(flag.rule_id, self.rule)

    def test_02_rule_defaults_and_counters(self):
        flag = self._flag()
        self.rule.invalidate_recordset()
        self.assertEqual(self.rule.flag_count, 1)
        self.assertEqual(self.rule.open_flag_count, 1)
        self.assertTrue(flag)

    def test_03_confirm_workflow(self):
        flag = self._flag(document_ref="BILL-AC-2026-002")
        self.assertTrue(flag.action_confirm())
        self.assertEqual(flag.state, "confirmed")
        self.rule.invalidate_recordset()
        self.assertEqual(self.rule.open_flag_count, 1)

    def test_04_resolve_workflow(self):
        flag = self._flag(document_ref="BILL-AC-2026-003")
        flag.action_confirm()
        self.assertTrue(flag.action_resolve())
        self.assertEqual(flag.state, "resolved")
        self.rule.invalidate_recordset()
        self.assertEqual(self.rule.open_flag_count, 0)

    def test_05_reject_workflow(self):
        flag = self._flag(document_ref="BILL-AC-2026-004")
        self.assertTrue(flag.action_reject())
        self.assertEqual(flag.state, "rejected")

    def test_06_double_confirm_is_refused(self):
        flag = self._flag(document_ref="BILL-AC-2026-005")
        flag.action_confirm()
        with self.assertRaises(ValidationError):
            flag.action_confirm()

    def test_07_amount_constraints(self):
        with self.assertRaises(ValidationError):
            self._flag(document_ref="BILL-AC-2026-006", total_amount=-1.0)
        with self.assertRaises(ValidationError):
            self._flag(document_ref="BILL-AC-2026-007", tax_amount=-5.0)
        with self.assertRaises(ValidationError):
            self._flag(document_ref="BILL-AC-2026-008",
                       tax_amount=50.0, total_amount=40.0)

    def test_08_quantity_constraint(self):
        with self.assertRaises(ValidationError):
            self._flag(document_ref="BILL-AC-2026-009", quantity=0)
        with self.assertRaises(ValidationError):
            self._flag(document_ref="BILL-AC-2026-010", quantity=-3)

    def test_09_resolve_closed_is_refused(self):
        flag = self._flag(document_ref="BILL-AC-2026-011")
        flag.action_resolve()
        with self.assertRaises(ValidationError):
            flag.action_resolve()

    def test_10_company_isolation(self):
        foreign = self.env["anomaly.rule"].with_company(
            self.other_company).create({
            "name": "AnomalyCheck Foreign Rule",
            "rule_type": "vat",
            "company_id": self.other_company.id,
        })
        foreign_flag = self.env["anomaly.flag"].with_company(
            self.other_company).create({
            "name": "AnomalyCheck Foreign Flag",
            "rule_id": foreign.id,
            "document_ref": "BILL-AC-FOREIGN-2026-001",
            "quantity": 1.0,
            "tax_amount": 10.0,
            "total_amount": 110.0,
            "flag_date": "2026-04-01",
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(foreign_flag.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.rule.company_id)
