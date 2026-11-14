# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCustomerVisitReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Visit Customer"})
        cls.manager = cls._user(
            "visitreport-manager", ["customer_visit_report.group_customervisi_user"])
        cls.outsider = cls._user(
            "visitreport-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _report(self, **kw):
        vals = {
            "partner_id": self.partner.id,
            "purpose": "Regular check-in",
            "summary": "Discussed needs",
            "company_id": self.env.company.id,
        }
        vals.update(kw)
        return self.env["customer.visit.report"].create(vals)

    def test_01_flow_submit_review(self):
        r = self._report()
        self.assertEqual(r.state, "draft")
        r.action_submit()
        self.assertEqual(r.state, "submitted")
        r.action_review()
        self.assertEqual(r.state, "reviewed")
        r.action_reset()
        self.assertEqual(r.state, "draft")

    def test_02_invalid_transitions(self):
        r = self._report()
        with self.assertRaises(UserError):
            r.action_review()
        r.action_submit()
        with self.assertRaises(UserError):
            r.action_submit()

    def test_03_followup_fields(self):
        r = self._report(followup_needed=True, followup_action="Send quote")
        self.assertTrue(r.followup_needed)
        self.assertEqual(r.followup_action, "Send quote")

    def test_04_access_control(self):
        r = self._report()
        with self.assertRaises(Exception):
            self.env["customer.visit.report"].with_user(self.outsider).create({
                "partner_id": self.partner.id,
                "purpose": "No access",
                "company_id": self.env.company.id,
            })
        r.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Visit B"})
        partner_b = self.env["res.partner"].create({"name": "Cust B", "company_id": company_b.id})
        foreign = self.env["customer.visit.report"].create({
            "partner_id": partner_b.id,
            "purpose": "Foreign",
            "company_id": company_b.id,
        })
        visible = self.env["customer.visit.report"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
