# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestQualityInspectionLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({
            "name": "Test Product", "type": "consu",
        })
        cls.manager = cls._user(
            "qil-manager",
            ["quality_inspection_log.group_qualityinspe_user"])
        cls.outsider = cls._user("qil-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "groups_id" if "groups_id" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _inspection(self, **vals):
        data = {
            "name": vals.pop("name", "QIL-TEST"),
            "product_id": self.product.id,
            "inspection_date": fields.Date.context_today(self.env.user),
            "company_id": self.env.company.id,
        }
        data.update(vals)
        return self.env["quality.inspection.log"].create(data)

    def test_01_create_inspection(self):
        rec = self._inspection()
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.result, "pending")

    def test_02_pass_flow(self):
        rec = self._inspection()
        rec.action_start()
        self.assertEqual(rec.state, "progress")
        rec.action_pass()
        self.assertEqual(rec.state, "passed")
        self.assertEqual(rec.result, "pass")

    def test_03_fail_and_reset(self):
        rec = self._inspection()
        rec.action_start()
        rec.action_fail()
        self.assertEqual(rec.state, "failed")
        self.assertEqual(rec.result, "fail")
        rec.action_reset_draft()
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.result, "pending")

    def test_04_invalid_transitions(self):
        rec = self._inspection()
        with self.assertRaises(UserError):
            rec.action_pass()
        rec.action_start()
        rec.action_pass()
        with self.assertRaises(UserError):
            rec.action_cancel()

    def test_05_access_control(self):
        with self.assertRaises(Exception):
            self.env["quality.inspection.log"].with_user(
                self.outsider).create({
                    "name": "NO",
                    "product_id": self.product.id,
                    "company_id": self.env.company.id,
                })
        rec = self._inspection(name="QIL-ACC")
        rec.with_user(self.manager).read()

    def test_06_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "QIL B"})
        foreign = self.env["quality.inspection.log"].create({
            "name": "QIL-FOREIGN",
            "product_id": self.product.id,
            "company_id": company_b.id,
        })
        visible = self.env["quality.inspection.log"].with_user(
            self.manager).search([])
        self.assertNotIn(foreign, visible)
