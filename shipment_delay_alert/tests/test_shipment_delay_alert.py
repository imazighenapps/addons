# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestShipmentDelayAlert(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Late Customer", "is_company": True,
            "customer_rank": 1,
        })
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.src = (cls.picking_type.default_location_src_id
                   or cls.env.ref("stock.stock_location_stock"))
        cls.dest = (cls.picking_type.default_location_dest_id
                    or cls.env.ref("stock.stock_location_customers"))
        cls.manager = cls._user(
            "dly-manager", ["shipment_delay_alert.group_shipmentdela_user"])
        cls.outsider = cls._user("dly-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _picking(self, days_late=3, cancel=False):
        picking = self.env["stock.picking"].create({
            "picking_type_id": self.picking_type.id,
            "partner_id": self.partner.id,
            "location_id": self.src.id,
            "location_dest_id": self.dest.id,
            "scheduled_date": fields.Datetime.now()
            - timedelta(days=days_late),
        })
        if cancel:
            picking.action_cancel()
        return picking

    def _scan(self, pickings=None):
        wizard = self.env["shipment.delay.scan"].create({
            "as_of": fields.Datetime.now(),
        })
        wizard.action_scan()
        domain = [("picking_id", "in", pickings.ids)] if pickings else []
        return self.env["shipment.delay.alert"].search(domain)

    def test_01_late_picking_gets_an_alert(self):
        picking = self._picking(4)
        alerts = self._scan(picking)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts.picking_id, picking)
        self.assertEqual(alerts.partner_id, self.partner)
        self.assertGreaterEqual(alerts.delay_days, 3)

    def test_02_picking_in_the_future_is_ignored(self):
        picking = self._picking(days_late=-5)
        self.assertFalse(self._scan(picking))

    def test_03_cancelled_picking_is_ignored(self):
        picking = self._picking(2, cancel=True)
        self.assertFalse(self._scan(picking))

    def test_04_scanning_twice_does_not_duplicate(self):
        picking = self._picking(2)
        first = self._scan(picking)
        second = self._scan(picking)
        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)

    def test_05_follow_up_statuses(self):
        picking = self._picking(2)
        alert = self._scan(picking)
        alert.action_contacted()
        self.assertEqual(alert.state, "contacted")
        alert.action_resolve()
        self.assertEqual(alert.state, "resolved")
        alert.action_reopen()
        self.assertEqual(alert.state, "open")
        alert.action_dismiss()
        self.assertEqual(alert.state, "dismissed")
        with self.assertRaises(UserError):
            alert.action_contacted()

    def test_06_access_control(self):
        picking = self._picking(2)
        with self.assertRaises(Exception):
            self.env["shipment.delay.alert"].with_user(self.outsider).create({
                "picking_id": picking.id,
                "company_id": self.env.company.id,
            })
        alert = self._scan(picking)
        alert.with_user(self.manager).read()

    def test_07_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Late B"})
        picking = self._picking(2)
        foreign = self.env["shipment.delay.alert"].create({
            "picking_id": picking.id,
            "company_id": company_b.id,
        })
        visible = self.env["shipment.delay.alert"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
