# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCloseFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env["close.template"].create({
            "name": "Monthly close",
        })
        cls.bank = cls.env["close.template.line"].create({
            "template_id": cls.template.id,
            "sequence": 10,
            "name": "Bank reconciliation",
            "due_day": 5,
            "evidence_required": True,
        })
        cls.vat = cls.env["close.template.line"].create({
            "template_id": cls.template.id,
            "sequence": 20,
            "name": "VAT return",
            "due_day": 10,
            "dependency_ids": [(6, 0, [cls.bank.id])],
        })
        cls.report = cls.env["close.template.line"].create({
            "template_id": cls.template.id,
            "sequence": 30,
            "name": "Management report",
            "due_day": 15,
        })

    def _period(self):
        return self.env["close.period"].create({
            "template_id": self.template.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 1, 31),
        })

    def _task(self, period, name):
        return period.task_ids.filtered(lambda task: task.name == name)

    def _proof(self, task):
        attachment = self.env["ir.attachment"].create({
            "name": "proof.txt", "raw": b"proof",
        })
        task.attachment_ids = [(4, attachment.id)]
        return attachment

    def test_01_generate(self):
        period = self._period()
        self.assertTrue(period.name.startswith("CLS/"))
        period.action_generate()
        self.assertEqual(len(period.task_ids), 3)
        self.assertEqual(period.state, "in_progress")
        bank = self._task(period, "Bank reconciliation")
        self.assertEqual(bank.due_date, date(2026, 2, 5))
        self.assertTrue(bank.evidence_required)
        vat = self._task(period, "VAT return")
        self.assertEqual(vat.dependency_ids, bank)
        self.assertEqual(period.progress, 0.0)

    def test_02_generate_twice_no_duplicate(self):
        period = self._period()
        period.action_generate()
        period.action_generate()
        self.assertEqual(len(period.task_ids), 3)

    def test_03_evidence_required(self):
        period = self._period()
        period.action_generate()
        bank = self._task(period, "Bank reconciliation")
        bank.action_start()
        self.assertEqual(bank.state, "in_progress")
        with self.assertRaises(UserError):
            bank.action_done()
        self._proof(bank)
        bank.action_done()
        self.assertEqual(bank.state, "done")
        self.assertTrue(bank.completed_on)
        self.assertTrue(bank.completed_by)
        self.assertAlmostEqual(period.progress, 33.33, places=1)

    def test_04_dependency_blocks(self):
        period = self._period()
        period.action_generate()
        vat = self._task(period, "VAT return")
        with self.assertRaises(UserError):
            vat.action_done()
        bank = self._task(period, "Bank reconciliation")
        self._proof(bank)
        bank.action_done()
        vat.action_done()
        self.assertEqual(vat.state, "done")

    def test_05_period_lock(self):
        period = self._period()
        period.action_generate()
        bank = self._task(period, "Bank reconciliation")
        self._proof(bank)
        bank.action_done()
        with self.assertRaises(UserError):
            period.action_done()
        self._task(period, "VAT return").action_done()
        self._task(period, "Management report").action_done()
        self.assertEqual(period.progress, 100.0)
        period.action_done()
        self.assertEqual(period.state, "done")
        period.action_lock()
        self.assertEqual(period.state, "locked")
        self.assertTrue(period.locked_on)
        with self.assertRaises(UserError):
            bank.write({"name": "Changed"})
        with self.assertRaises(UserError):
            self.env["close.task"].create({
                "period_id": period.id, "name": "Extra",
            })
        period.action_unlock()
        self.assertEqual(period.state, "in_progress")
        bank.write({"name": "Changed"})

    def test_06_unlock_requires_manager(self):
        user = self.env["res.users"].create({
            "name": "Close User",
            "login": "close_user_test",
            "email": "close.user@example.com",
            "groups_id": [(6, 0, [
                self.env.ref("close_flow.group_closeflow_user").id])],
        })
        period = self._period()
        period.action_generate()
        bank = self._task(period, "Bank reconciliation")
        self._proof(bank)
        bank.action_done()
        self._task(period, "VAT return").action_done()
        self._task(period, "Management report").action_done()
        period.action_done()
        period.action_lock()
        with self.assertRaises(UserError):
            period.with_user(user).action_unlock()

    def test_07_blocked_task(self):
        period = self._period()
        period.action_generate()
        report = self._task(period, "Management report")
        with self.assertRaises(UserError):
            report.action_block()
        report.blocked_reason = "Waiting for the CFO"
        report.action_block()
        self.assertEqual(report.state, "blocked")
        report.action_start()
        self.assertEqual(report.state, "in_progress")
        self.assertFalse(report.blocked_reason)

    def test_08_template_self_dependency(self):
        with self.assertRaises(Exception):
            self.bank.dependency_ids = [(4, self.bank.id)]

    def test_09_task_dependency_other_period(self):
        first = self._period()
        first.action_generate()
        second = self._period()
        second.action_generate()
        task = self._task(second, "Management report")
        with self.assertRaises(Exception):
            task.dependency_ids = [(4, self._task(
                first, "VAT return").id)]

    def test_10_reopen_task(self):
        period = self._period()
        period.action_generate()
        report = self._task(period, "Management report")
        report.action_done()
        self.assertEqual(report.state, "done")
        report.action_reopen()
        self.assertEqual(report.state, "todo")
        self.assertFalse(report.completed_on)
