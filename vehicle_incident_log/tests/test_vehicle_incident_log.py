# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVehicleIncidentLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vehicle = cls.env["fleet.vehicle"].create({"model_id": cls.env["fleet.vehicle.model"].search([], limit=1).id or cls.env["fleet.vehicle.model"].create({"name": "Demo", "brand_id": cls.env["fleet.vehicle.model.brand"].search([], limit=1).id or cls.env["fleet.vehicle.model.brand"].create({"name": "Brand"}).id}).id})
        cls.manager = cls._user(
            "vehinc-manager", ["vehicle_incident_log.group_vehicleincid_user"])
        cls.outsider = cls._user(
            "vehinc-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _rec(self):
        return self.env["vehicle.incident.log"].create({
            "vehicle_id": self.vehicle.id,
            "location": "Parking lot",
            "description": "Minor scratch.",
            "company_id": self.env.company.id,
        })

    def test_01_flow_report_progress_close(self):
        r = self._rec()
        r.action_report()
        self.assertEqual(r.state, "reported")
        r.action_start()
        self.assertEqual(r.state, "in_progress")
        r.action_close()
        self.assertEqual(r.state, "closed")

    def test_02_state_guards(self):
        r = self._rec()
        with self.assertRaises(UserError):
            r.action_start()
        r.action_report()
        with self.assertRaises(UserError):
            r.action_report()

    def test_03_access_control(self):
        r = self._rec()
        with self.assertRaises(Exception):
            self.env["vehicle.incident.log"].with_user(self.outsider).create({
                "vehicle_id": self.vehicle.id,
                "location": "X",
                "description": "No",
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_04_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "VehInc B"})
        foreign = self.env["vehicle.incident.log"].create({
            "vehicle_id": self.vehicle.id,
            "location": "B",
            "description": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["vehicle.incident.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)

    def test_05_reset(self):
        r = self._rec()
        r.action_report()
        r.action_close()
        r.action_reset()
        self.assertEqual(r.state, "draft")
