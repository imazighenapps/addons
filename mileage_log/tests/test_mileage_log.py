# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMileageLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Mileage Employee"})
        cls.manager = cls._user(
            "mileage-manager", ["mileage_log.group_mileagelog_user"])
        cls.outsider = cls._user(
            "mileage-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _log(self, distance=20.0, rate=0.5):
        return self.env["mileage.log"].create({
            "employee_id": self.employee.id,
            "purpose": "Client visit",
            "distance": distance,
            "rate": rate,
            "company_id": self.env.company.id,
        })

    def test_01_flow_validate(self):
        m = self._log()
        self.assertAlmostEqual(m.amount, 10.0)
        m.action_submit()
        m.action_validate()
        self.assertEqual(m.state, "validated")

    def test_02_refuse(self):
        m = self._log()
        m.action_submit()
        m.action_refuse()
        self.assertEqual(m.state, "refused")

    def test_03_state_guards(self):
        m = self._log()
        with self.assertRaises(UserError):
            m.action_validate()
        m.action_submit()
        with self.assertRaises(UserError):
            m.action_submit()

    def test_04_validation(self):
        with self.assertRaises(ValidationError):
            self._log(distance=0.0)
        with self.assertRaises(ValidationError):
            self._log(rate=-1.0)

    def test_05_access_control(self):
        m = self._log()
        with self.assertRaises(Exception):
            self.env["mileage.log"].with_user(self.outsider).create({
                "employee_id": self.employee.id,
                "purpose": "No",
                "distance": 5.0,
                "rate": 0.5,
                "company_id": self.env.company.id,
            })
        m.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Mil B"})
        emp_b = self.env["hr.employee"].create({"name": "Emp B", "company_id": company_b.id})
        foreign = self.env["mileage.log"].create({
            "employee_id": emp_b.id,
            "purpose": "Foreign",
            "distance": 10.0,
            "rate": 0.5,
            "company_id": company_b.id,
        })
        visible = self.env["mileage.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
