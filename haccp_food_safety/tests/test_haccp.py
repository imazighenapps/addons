# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHaccp(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan = cls.env["haccp.plan"].create({"name": "Demo Dairy Plan", "version": "1.0"})
        cls.ccp = cls.env["haccp.ccp"].create({
            "name": "Cold Room", "code": "CCP-1", "plan_id": cls.plan.id,
            "hazard_type": "bio", "limit_min": 0.0, "limit_max": 4.0,
            "uom_id": cls.env.ref("uom.product_uom_unit").id,
        })

    def test_01_seed(self):
        self.assertEqual(len(self.env["haccp.allergen"].search([])), 14)
        # scope to our own plan: a customer who already set up CCPs must
        # not fail the module's test suite
        self.assertEqual(
            len(self.env["haccp.ccp"].search([("plan_id", "=", self.plan.id)])), 1)

    def test_02_reading_ok_ko(self):
        ok = self.env["haccp.reading"].create(
            {"ccp_id": self.ccp.id, "value": 2.5})
        self.assertEqual(ok.result, "ok")
        ko = self.env["haccp.reading"].create(
            {"ccp_id": self.ccp.id, "value": 9.0})
        self.assertEqual(ko.result, "ko")
        ko.action_create_nc()
        self.assertTrue(ko.nc_id)
        self.assertEqual(ko.nc_id.severity, "major")

    def test_03_nc_workflow(self):
        nc = self.env["haccp.nonconformity"].create({"name": "Broken seal"})
        for state in ("open", "action", "verify"):
            getattr(nc, "action_" + ("open" if state == "open" else
                                     "start" if state == "action" else "verify"))()
            self.assertEqual(nc.state, state)
        nc.action_close()
        self.assertEqual(nc.state, "closed")
        self.assertTrue(nc.closed_date)

    def test_04_plan_validate(self):
        self.plan.action_validate()
        self.assertEqual(self.plan.state, "validated")
        self.assertTrue(self.plan.validated_on)

    def test_05_product_allergens(self):
        milk = self.env.ref("haccp_food_safety.allergen_milk")
        tmpl = self.env["product.template"].create({"name": "Demo Cheese", "type": "consu"})
        tmpl.write({"allergen_ids": [(6, 0, milk.ids)]})
        self.assertIn(milk, tmpl.allergen_ids)

    def test_06_expiry_cron(self):
        self.env["haccp.expiry.alert"]._cron_check_expiry()
