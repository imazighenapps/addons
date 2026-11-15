# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSupplierVisitLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env["res.partner"].create({"name": "Visit Supplier", "supplier_rank": 1})
        cls.manager = cls._user(
            "supvisit-manager", ["supplier_visit_log.group_suppliervisi_user"])
        cls.outsider = cls._user(
            "supvisit-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _visit(self):
        return self.env["supplier.visit.log"].create({
            "partner_id": self.supplier.id,
            "purpose": "Quality audit",
            "findings": "Process documented.",
            "company_id": self.env.company.id,
        })

    def test_01_flow_submit_review(self):
        v = self._visit()
        v.action_submit()
        self.assertEqual(v.state, "submitted")
        v.action_review()
        self.assertEqual(v.state, "reviewed")
        v.action_reset()
        self.assertEqual(v.state, "draft")

    def test_02_state_guards(self):
        v = self._visit()
        with self.assertRaises(UserError):
            v.action_review()
        v.action_submit()
        with self.assertRaises(UserError):
            v.action_submit()

    def test_03_access_control(self):
        v = self._visit()
        with self.assertRaises(Exception):
            self.env["supplier.visit.log"].with_user(self.outsider).create({
                "partner_id": self.supplier.id,
                "purpose": "No",
                "company_id": self.env.company.id,
            })
        v.with_user(self.manager).read()

    def test_04_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "SupVisit B"})
        sup_b = self.env["res.partner"].create({"name": "SB", "supplier_rank": 1, "company_id": company_b.id})
        foreign = self.env["supplier.visit.log"].create({
            "partner_id": sup_b.id,
            "purpose": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["supplier.visit.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)

    def test_05_fields(self):
        v = self._visit()
        self.assertEqual(v.purpose, "Quality audit")
        self.assertTrue(v.name)
