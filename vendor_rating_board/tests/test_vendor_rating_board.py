# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVendorRatingBoard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env["res.partner"].create({
            "name": "Test Supplier", "supplier_rank": 1,
        })
        cls.manager = cls._user(
            "vrb-manager", ["vendor_rating_board.group_vendorrating_user"])
        cls.outsider = cls._user("vrb-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _eval(self, **vals):
        data = {
            "name": vals.pop("name", "VE-TEST"),
            "partner_id": self.supplier.id,
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["vendor.evaluation"].create(data)

    def test_01_overall_score_computed(self):
        evaluation = self._eval(
            delivery_score=4, quality_score=2, price_score=5, service_score=3)
        self.assertAlmostEqual(evaluation.overall_score, 3.5, places=2)

    def test_02_state_flow(self):
        evaluation = self._eval()
        evaluation.action_validate()
        self.assertEqual(evaluation.state, "validated")
        evaluation.action_archive_eval()
        self.assertEqual(evaluation.state, "archived")
        evaluation.action_reset_draft()
        self.assertEqual(evaluation.state, "draft")

    def test_03_invalid_state_transitions(self):
        evaluation = self._eval()
        with self.assertRaises(UserError):
            evaluation.action_archive_eval()
        evaluation.action_validate()
        with self.assertRaises(UserError):
            evaluation.action_validate()

    def test_04_score_out_of_range_is_refused(self):
        with self.assertRaises(ValidationError):
            self._eval(delivery_score=6)
        with self.assertRaises(ValidationError):
            self._eval(quality_score=-1)

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["vendor.evaluation"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "partner_id": self.supplier.id,
                    "company_id": self.env.company.id,
                })
        evaluation = self._eval(name="VE-ACC")
        evaluation.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "VRB B"})
        foreign = self.env["vendor.evaluation"].create({
            "name": "VE-FOREIGN",
            "partner_id": self.supplier.id,
            "company_id": company_b.id,
        })
        visible = self.env["vendor.evaluation"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
