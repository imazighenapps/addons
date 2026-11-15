# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCleaningLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Cleaner"})
        cls.manager = cls._user(
            "clean-manager", ["cleaning_log.group_cleaninglog_user"])
        cls.outsider = cls._user(
            "clean-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _task(self):
        return self.env["cleaning.log"].create({
            "area": "Lobby",
            "task": "Floor mopping",
            "responsible_id": self.employee.id,
            "company_id": self.env.company.id,
        })

    def test_01_done(self):
        t = self._task()
        t.action_done()
        self.assertEqual(t.state, "done")
        self.assertTrue(t.date_done)

    def test_02_missed(self):
        t = self._task()
        t.action_missed()
        self.assertEqual(t.state, "missed")

    def test_03_state_guards(self):
        t = self._task()
        t.action_done()
        with self.assertRaises(UserError):
            t.action_missed()
        with self.assertRaises(UserError):
            t.action_cancel()

    def test_04_access_control(self):
        t = self._task()
        with self.assertRaises(Exception):
            self.env["cleaning.log"].with_user(self.outsider).create({
                "area": "X",
                "task": "No",
                "company_id": self.env.company.id,
            })
        t.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Clean B"})
        foreign = self.env["cleaning.log"].create({
            "area": "B",
            "task": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["cleaning.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
