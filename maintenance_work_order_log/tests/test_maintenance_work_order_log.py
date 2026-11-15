# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMaintenanceWorkOrderLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env["maintenance.equipment"].create({
            "name": "Test Equipment",
        })
        cls.manager = cls._user(
            "mwo-manager",
            ["maintenance_work_order_log.group_maintenancew_user"])
        cls.outsider = cls._user("mwo-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _order(self, **vals):
        data = {
            "name": vals.pop("name", "MWO-TEST"),
            "equipment_id": self.equipment.id,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["maintenance.work.order.log"].create(data)

    def test_01_create_order(self):
        order = self._order()
        self.assertEqual(order.state, "draft")
        self.assertEqual(order.equipment_id, self.equipment)

    def test_02_state_flow(self):
        order = self._order()
        order.action_start()
        self.assertEqual(order.state, "progress")
        self.assertTrue(order.date_start)
        order.action_done()
        self.assertEqual(order.state, "done")
        self.assertTrue(order.date_end)

    def test_03_cancel_and_reset(self):
        order = self._order()
        order.action_cancel()
        self.assertEqual(order.state, "cancelled")
        order.action_reset_draft()
        self.assertEqual(order.state, "draft")
        self.assertFalse(order.date_start)

    def test_04_invalid_transitions(self):
        order = self._order()
        with self.assertRaises(UserError):
            order.action_done()
        order.action_start()
        order.action_done()
        with self.assertRaises(UserError):
            order.action_cancel()

    def test_05_end_before_start_is_refused(self):
        now = fields.Datetime.now()
        with self.assertRaises(ValidationError):
            self._order(date_start=now, date_end=now - timedelta(hours=1))

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["maintenance.work.order.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "equipment_id": self.equipment.id,
                    "company_id": self.env.company.id,
                })
        order = self._order(name="MWO-ACC")
        order.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "MWO B"})
        foreign = self.env["maintenance.work.order.log"].create({
            "name": "MWO-FOREIGN",
            "equipment_id": self.equipment.id,
            "company_id": company_b.id,
        })
        visible = self.env["maintenance.work.order.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
