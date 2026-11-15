# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFuelRequestLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        brand = cls.env["fleet.vehicle.model.brand"].create({"name": "TBrand"})
        model = cls.env["fleet.vehicle.model"].create({
            "name": "TModel", "brand_id": brand.id, "vehicle_type": "car",
        })
        cls.vehicle = cls.env["fleet.vehicle"].create({
            "model_id": model.id, "license_plate": "TST-123",
        })
        cls.manager = cls._user(
            "frl-manager",
            ["fuel_request_log.group_fuelrequestl_user"])
        cls.outsider = cls._user("frl-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _req(self, **vals):
        data = {
            "name": vals.pop("name", "FRL-TEST"),
            "vehicle_id": self.vehicle.id,
            "request_date": fields.Date.context_today(self.env.user),
            "amount": 50.0,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["fuel.request.log"].create(data)

    def test_01_create_request(self):
        rec = self._req()
        self.assertEqual(rec.state, "draft")

    def test_02_approve_fulfill_flow(self):
        rec = self._req()
        rec.action_submit()
        self.assertEqual(rec.state, "submitted")
        rec.action_approve()
        self.assertEqual(rec.state, "approved")
        rec.action_fulfill()
        self.assertEqual(rec.state, "fulfilled")

    def test_03_reject_and_reset(self):
        rec = self._req()
        rec.action_submit()
        rec.action_reject()
        self.assertEqual(rec.state, "rejected")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")

    def test_04_invalid_transitions(self):
        rec = self._req()
        with self.assertRaises(UserError):
            rec.action_approve()
        rec.action_submit()
        with self.assertRaises(UserError):
            rec.action_fulfill()

    def test_05_amount_validation(self):
        with self.assertRaises(ValidationError):
            self._req(amount=0)

    def test_06_access_control(self):
        with self.assertRaises(Exception):
            self.env["fuel.request.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "vehicle_id": self.vehicle.id,
                    "amount": 10.0,
                    "company_id": self.env.company.id,
                })
        rec = self._req(name="FRL-ACC")
        rec.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "FRL B"})
        foreign = self.env["fuel.request.log"].create({
            "name": "FRL-FOREIGN",
            "vehicle_id": self.vehicle.id,
            "amount": 20.0,
            "company_id": company_b.id,
        })
        visible = self.env["fuel.request.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
