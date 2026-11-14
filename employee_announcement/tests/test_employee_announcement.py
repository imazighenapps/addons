# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEmployeeAnnouncement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "announce-manager", ["employee_announcement.group_employeeanno_user"])
        cls.outsider = cls._user(
            "announce-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _ann(self, **kw):
        vals = {
            "name": "Test Announcement",
            "body": "<p>Hello team</p>",
            "company_id": self.env.company.id,
        }
        vals.update(kw)
        return self.env["employee.announcement"].create(vals)

    def test_01_publish_and_archive(self):
        a = self._ann()
        a.action_publish()
        self.assertEqual(a.state, "published")
        a.action_archive_announcement()
        self.assertEqual(a.state, "archived")

    def test_02_archived_cannot_publish(self):
        a = self._ann()
        a.action_archive_announcement()
        with self.assertRaises(UserError):
            a.action_publish()

    def test_03_expiry_flag(self):
        today = fields.Date.context_today(self.env.user)
        a = self._ann(date_publish=today - timedelta(days=10), date_expiry=today - timedelta(days=1))
        self.assertTrue(a.is_expired)

    def test_04_date_validation(self):
        today = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self._ann(date_publish=today, date_expiry=today - timedelta(days=1))

    def test_05_access_control(self):
        a = self._ann()
        with self.assertRaises(Exception):
            self.env["employee.announcement"].with_user(self.outsider).create({
                "name": "No", "body": "<p>x</p>", "company_id": self.env.company.id,
            })
        a.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Ann B"})
        foreign = self.env["employee.announcement"].create({
            "name": "Foreign", "body": "<p>x</p>", "company_id": company_b.id,
        })
        visible = self.env["employee.announcement"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
