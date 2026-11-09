# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHireCheck(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "HireCheck Other Company"})
        cls.employee = cls.env["hr.employee"].create({
            "name": "HireCheck Test Employee"})
        cls.employee_out = cls.env["hr.employee"].create({
            "name": "HireCheck Test Departure",
        })

    def _check(self, employee=None, **values):
        defaults = {
            "employee_id": (employee or self.employee).id,
            "kind": "onboarding",
        }
        defaults.update(values)
        return self.env["hire.check"].create(defaults)

    def test_01_starter_lines_are_pushed(self):
        check = self._check()
        self.assertEqual(check.state, "draft")
        self.assertEqual(check.line_count, 4)
        self.assertEqual(check.todo_count, 4)
        self.assertEqual(check.company_id, self.env.company)
        self.assertTrue(check.name.startswith("Check "))

    def test_02_offboarding_has_its_own_starter_lines(self):
        check = self._check(employee=self.employee_out,
                            kind="offboarding")
        self.assertEqual(check.line_count, 4)
        self.assertTrue(check.line_ids.filtered(
            lambda line: "badge" in line.name))

    def test_03_an_existing_list_is_left_alone(self):
        check = self._check(line_ids=[(0, 0, {
            "name": "HireCheck Test Custom Task"})])
        self.assertEqual(check.line_count, 1)
        self.assertEqual(check.todo_count, 1)

    def test_04_workflow(self):
        check = self._check()
        check.line_ids.action_done()
        self.assertEqual(check.todo_count, 0)
        self.assertTrue(check.action_start())
        self.assertEqual(check.state, "in_progress")
        self.assertTrue(check.action_done())
        self.assertEqual(check.state, "done")

    def test_05_start_twice_is_refused(self):
        check = self._check()
        check.action_start()
        with self.assertRaises(UserError):
            check.action_start()
        with self.assertRaises(UserError):
            self._check().action_done()

    def test_06_close_is_blocked_by_open_tasks(self):
        check = self._check()
        check.action_start()
        with self.assertRaises(UserError):
            check.action_done()
        check.line_ids.action_done()
        self.assertTrue(check.action_done())

    def test_07_reopen_and_cancel(self):
        check = self._check()
        check.line_ids.action_done()
        check.action_start()
        check.action_done()
        self.assertTrue(check.action_reopen())
        self.assertEqual(check.state, "in_progress")
        other = self._check()
        other.action_cancel()
        self.assertEqual(other.state, "cancelled")
        with self.assertRaises(UserError):
            other.line_ids.action_done()

    def test_08_task_defaults_and_reopen(self):
        task = self.env["hire.check.line"].create({
            "check_id": self._check().id,
            "name": "HireCheck Test Task",
        })
        self.assertEqual(task.responsible_id, self.env.user)
        self.assertEqual(task.category, "other")
        self.assertTrue(task.action_done())
        self.assertTrue(task.done_date)
        task.action_reopen()
        self.assertEqual(task.state, "todo")
        self.assertFalse(task.done_date)

    def test_09_company_isolation(self):
        foreign_employee = self.env["hr.employee"].sudo().create({
            "name": "HireCheck Test Foreign Employee",
        })
        foreign = self.env["hire.check"].with_company(
            self.other_company).sudo().create({
            "employee_id": foreign_employee.id,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._check()
        self.assertEqual(local.company_id, self.env.company)
