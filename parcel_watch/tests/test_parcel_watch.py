# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestParcelWatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ParcelWatch Other Company"})
        cls.supplier = cls.env["res.partner"].create({
            "name": "ParcelWatch Supplier"})
        cls.tomorrow = date(2026, 11, 12)
        cls.yesterday = date(2026, 11, 10)
        cls.today = date(2026, 11, 11)

    def _parcel(self, **values):
        defaults = {
            "name": "PW-TEST-001",
            "tracking_number": "1Z999PW001",
            "carrier": "dhl",
            "partner_id": self.supplier.id,
            "expected_on": self.tomorrow,
        }
        defaults.update(values)
        return self.env["parcel.parcel"].create(defaults)

    def test_01_defaults_and_reference(self):
        parcel = self._parcel()
        self.assertEqual(parcel.state, "draft")
        self.assertEqual(parcel.company_id, self.env.company)
        self.assertFalse(parcel.received_on)
        self.assertFalse(parcel.is_late)

    def test_02_tracking_url_computed(self):
        parcel = self._parcel(tracking_number="ABC123", carrier="ups")
        self.assertIn("ABC123", parcel.tracking_url)
        self.assertIn("ups.com", parcel.tracking_url)

    def test_03_in_transit_and_receive_flow(self):
        parcel = self._parcel()
        self.assertTrue(parcel.action_mark_in_transit())
        self.assertEqual(parcel.state, "in_transit")
        self.assertTrue(parcel.action_mark_received())
        self.assertEqual(parcel.state, "received")
        self.assertTrue(parcel.received_on)

    def test_04_lost_flow_and_reset(self):
        parcel = self._parcel(name="PW-TEST-LOST")
        parcel.action_mark_in_transit()
        self.assertTrue(parcel.action_mark_lost())
        self.assertEqual(parcel.state, "lost")
        self.assertTrue(parcel.action_reset_draft())
        self.assertEqual(parcel.state, "draft")
        self.assertFalse(parcel.received_on)

    def test_05_received_cannot_reset(self):
        parcel = self._parcel(name="PW-TEST-NORESET")
        parcel.action_mark_received()
        with self.assertRaises(ValidationError):
            parcel.action_reset_draft()

    def test_06_invalid_transitions(self):
        parcel = self._parcel(name="PW-TEST-INV")
        parcel.action_mark_in_transit()
        with self.assertRaises(ValidationError):
            parcel.action_mark_in_transit()

    def test_07_early_receipt_is_allowed(self):
        parcel = self._parcel(name="PW-TEST-DATE", expected_on=date(2026, 11, 15))
        parcel.write({"state": "received", "received_on": date(2026, 11, 10)})
        self.assertEqual(parcel.received_on, date(2026, 11, 10))

    def test_08_late_flag_stored(self):
        past = fields.Date.context_today(self.env["parcel.parcel"]) - timedelta(days=1)
        parcel = self._parcel(name="PW-TEST-LATE", expected_on=past)
        parcel.invalidate_recordset(["is_late"])
        self.assertTrue(parcel.is_late)
        parcel.action_mark_received()
        parcel.invalidate_recordset(["is_late"])
        self.assertFalse(parcel.is_late)

    def test_09_company_isolation(self):
        foreign = self.env["parcel.parcel"].with_company(
            self.other_company).create({
            "name": "PW-FOREIGN",
            "tracking_number": "FOR-001",
            "carrier": "fedex",
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._parcel(name="PW-LOCAL")
        self.assertNotEqual(local.company_id, foreign.company_id)
