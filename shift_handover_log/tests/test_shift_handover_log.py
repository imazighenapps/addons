# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestShiftHandoverLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.outgoing = cls.env["hr.employee"].create({"name": "Outgoing"})
        cls.incoming = cls.env["hr.employee"].create({"name": "Incoming"})
        cls.manager = cls._user(
            "handover-manager", ["shift_handover_log.group_shifthandove_user"])
        cls.outsider = cls._user(
            "handover-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _rec(self):
        return self.env["shift.handover.log"].create({
            "shift": "morning",
            "area": "Line A",
            "outgoing_id": self.outgoing.id,
            "incoming_id": self.incoming.id,
            "summary": "Normal operations.",
            "company_id": self.env.company.id,
        })

    def test_01_flow_submit_ack(self):
        r = self._rec()
        r.action_submit()
        self.assertEqual(r.state, "submitted")
        r.action_acknowledge()
        self.assertEqual(r.state, "acknowledged")

    def test_02_reset(self):
        r = self._rec()
        r.action_submit()
        r.action_acknowledge()
        r.action_reset()
        self.assertEqual(r.state, "draft")

    def test_03_state_guards(self):
        r = self._rec()
        with self.assertRaises(UserError):
            r.action_acknowledge()
        r.action_submit()
        with self.assertRaises(UserError):
            r.action_submit()

    def test_04_access_control(self):
        r = self._rec()
        with self.assertRaises(Exception):
            self.env["shift.handover.log"].with_user(self.outsider).create({
                "shift": "morning",
                "area": "X",
                "summary": "No",
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Shift B"})
        foreign = self.env["shift.handover.log"].create({
            "shift": "night",
            "area": "B",
            "summary": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["shift.handover.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
