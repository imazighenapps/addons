# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSoftwareLicense(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "license-manager", ["software_license.group_softwarelice_user"])
        cls.outsider = cls._user(
            "license-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _lic(self, **kw):
        vals = {
            "name": "Demo App",
            "vendor": "Acme",
            "seats": 5,
            "company_id": self.env.company.id,
        }
        vals.update(kw)
        return self.env["software.license"].create(vals)

    def test_01_mark_expired_and_reset(self):
        l = self._lic()
        l.action_mark_expired()
        self.assertEqual(l.state, "expired")
        l.action_reset()
        self.assertEqual(l.state, "active")

    def test_02_cancel(self):
        l = self._lic()
        l.action_cancel()
        self.assertEqual(l.state, "cancelled")
        with self.assertRaises(UserError):
            l.action_mark_expired()

    def test_03_expiry_flag(self):
        today = fields.Date.context_today(self.env.user)
        l = self._lic(date_expiry=today - timedelta(days=1))
        self.assertTrue(l.is_expired)

    def test_04_validation(self):
        with self.assertRaises(ValidationError):
            self._lic(seats=-1)
        today = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self._lic(date_purchase=today, date_expiry=today - timedelta(days=1))

    def test_05_access_control(self):
        l = self._lic()
        with self.assertRaises(Exception):
            self.env["software.license"].with_user(self.outsider).create({
                "name": "No",
                "company_id": self.env.company.id,
            })
        l.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Lic B"})
        foreign = self.env["software.license"].create({
            "name": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["software.license"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
