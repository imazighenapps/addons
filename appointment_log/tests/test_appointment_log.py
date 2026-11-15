# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAppointmentLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Appt Contact"})
        cls.manager = cls._user(
            "appt-manager", ["appointment_log.group_appointmentl_user"])
        cls.outsider = cls._user(
            "appt-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _appt(self):
        return self.env["appointment.log"].create({
            "name": "Intro meeting",
            "partner_id": self.partner.id,
            "company_id": self.env.company.id,
        })

    def test_01_flow_done(self):
        a = self._appt()
        a.action_done()
        self.assertEqual(a.state, "done")
        a.action_reset()
        self.assertEqual(a.state, "planned")

    def test_02_cancel(self):
        a = self._appt()
        a.action_cancel()
        self.assertEqual(a.state, "cancelled")

    def test_03_state_guards(self):
        a = self._appt()
        a.action_done()
        with self.assertRaises(UserError):
            a.action_done()
        a2 = self._appt()
        a2.action_done()
        with self.assertRaises(UserError):
            a2.action_cancel()

    def test_04_access_control(self):
        a = self._appt()
        with self.assertRaises(Exception):
            self.env["appointment.log"].with_user(self.outsider).create({
                "name": "No",
                "partner_id": self.partner.id,
                "company_id": self.env.company.id,
            })
        a.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Appt B"})
        partner_b = self.env["res.partner"].create({"name": "PB", "company_id": company_b.id})
        foreign = self.env["appointment.log"].create({
            "name": "Foreign",
            "partner_id": partner_b.id,
            "company_id": company_b.id,
        })
        visible = self.env["appointment.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
