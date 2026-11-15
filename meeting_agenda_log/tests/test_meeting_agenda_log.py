# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMeetingAgendaLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls._user(
            "magenda-manager", ["meeting_agenda_log.group_meetingagend_user"])
        cls.outsider = cls._user("magenda-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _rec(self):
        return self.env["meeting.agenda.log"].create({
            "name": "Team Sync",
            "agenda": "Discuss progress",
            "company_id": self.env.company.id,
        })

    def test_01_plan_done(self):
        r = self._rec()
        r.action_plan()
        self.assertEqual(r.state, "planned")
        r.action_done()
        self.assertEqual(r.state, "done")

    def test_02_cancel(self):
        r = self._rec()
        r.action_cancel()
        self.assertEqual(r.state, "cancelled")

    def test_03_state_guards(self):
        r = self._rec()
        r.action_plan()
        with self.assertRaises(UserError):
            r.action_plan()

    def test_04_access_control(self):
        r = self._rec()
        with self.assertRaises(Exception):
            self.env["meeting.agenda.log"].with_user(self.outsider).create({
                "name": "No",
                "agenda": "No",
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "MA B"})
        foreign = self.env["meeting.agenda.log"].create({
            "name": "Foreign",
            "agenda": "Foreign agenda",
            "company_id": company_b.id,
        })
        visible = self.env["meeting.agenda.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
