# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOfficeSupplyRequest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Supply Employee"})
        cls.manager = cls._user(
            "supply-manager", ["office_supply_request.group_officesupply_user"])
        cls.outsider = cls._user(
            "supply-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _req(self):
        return self.env["office.supply.request"].create({
            "employee_id": self.employee.id,
            "company_id": self.env.company.id,
            "line_ids": [(0, 0, {"name": "Pens", "quantity": 10.0})],
        })

    def test_01_flow_submit_approve_fulfill(self):
        r = self._req()
        r.action_submit()
        self.assertEqual(r.state, "submitted")
        r.action_approve()
        self.assertEqual(r.state, "approved")
        r.action_fulfill()
        self.assertEqual(r.state, "fulfilled")

    def test_02_submit_requires_lines(self):
        r = self.env["office.supply.request"].create({"company_id": self.env.company.id})
        with self.assertRaises(UserError):
            r.action_submit()

    def test_03_state_guards(self):
        r = self._req()
        with self.assertRaises(UserError):
            r.action_approve()
        r.action_submit()
        with self.assertRaises(UserError):
            r.action_fulfill()

    def test_04_line_validation(self):
        with self.assertRaises(ValidationError):
            self.env["office.supply.request"].create({
                "company_id": self.env.company.id,
                "line_ids": [(0, 0, {"name": "Bad", "quantity": 0.0})],
            })

    def test_05_access_control(self):
        r = self._req()
        with self.assertRaises(Exception):
            self.env["office.supply.request"].with_user(self.outsider).create({
                "company_id": self.env.company.id,
                "line_ids": [(0, 0, {"name": "X", "quantity": 1.0})],
            })
        r.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Supply B"})
        foreign = self.env["office.supply.request"].create({
            "company_id": company_b.id,
            "line_ids": [(0, 0, {"name": "Foreign", "quantity": 1.0})],
        })
        visible = self.env["office.supply.request"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
