# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDonationLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.donor = cls.env["res.partner"].create({"name": "Demo Donor"})
        cls.manager = cls._user(
            "donation-manager", ["donation_log.group_donationlog_user"])
        cls.outsider = cls._user(
            "donation-outsider", ["base.group_user"])

    @classmethod
    def _user(cls, login, group_refs):
        groups = [cls.env.ref(ref).id for ref in group_refs]
        field = "group_ids" if "group_ids" in cls.env["res.users"]._fields else "groups_id"
        return cls.env["res.users"].create({
            "name": login, "login": login, field: [(6, 0, groups)],
        })

    def _don(self, amount=50.0):
        return self.env["donation.log"].create({
            "donor_id": self.donor.id,
            "amount": amount,
            "purpose": "General",
            "company_id": self.env.company.id,
        })

    def test_01_flow_receive_ack(self):
        d = self._don()
        d.action_receive()
        self.assertEqual(d.state, "received")
        d.action_acknowledge()
        self.assertEqual(d.state, "acknowledged")

    def test_02_state_guards(self):
        d = self._don()
        with self.assertRaises(UserError):
            d.action_acknowledge()
        d.action_receive()
        with self.assertRaises(UserError):
            d.action_receive()

    def test_03_amount_validation(self):
        with self.assertRaises(ValidationError):
            self._don(amount=0.0)

    def test_04_access_control(self):
        d = self._don()
        with self.assertRaises(Exception):
            self.env["donation.log"].with_user(self.outsider).create({
                "donor_id": self.donor.id,
                "amount": 10.0,
                "company_id": self.env.company.id,
            })
        d.with_user(self.manager).read()

    def test_05_company_isolation(self):
        company_b = self.env["res.company"].create({"name": "Don B"})
        donor_b = self.env["res.partner"].create({"name": "Donor B", "company_id": company_b.id})
        foreign = self.env["donation.log"].create({
            "donor_id": donor_b.id,
            "amount": 20.0,
            "company_id": company_b.id,
        })
        visible = self.env["donation.log"].with_user(self.manager).search([])
        self.assertNotIn(foreign, visible)
