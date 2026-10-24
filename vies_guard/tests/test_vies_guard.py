# -*- coding: utf-8 -*-
from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

PATCH = "odoo.addons.vies_guard.models.vies_guard.vies_query"
VALID = {"isValid": True, "name": "ACME FRANCE", "address": "1 rue de Paris",
         "userError": "VALID"}
INVALID = {"isValid": False, "name": "", "address": "",
           "userError": "INVALID"}


@tagged("post_install", "-at_install")
class TestViesGuard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.france = cls.env.ref("base.fr")
        cls.usa = cls.env.ref("base.us")

    def _partner(self, vat, country=None, name="VAT Customer"):
        return self.env["res.partner"].create({
            "name": name,
            "vat": vat,
            "country_id": (country or self.france).id,
        })

    def test_01_valid_vat(self):
        with patch(PATCH, return_value=VALID):
            partner = self._partner("FR 23 334 175 221")
        self.assertEqual(partner.vies_state, "valid")
        self.assertEqual(partner.vies_trader_name, "ACME FRANCE")
        self.assertTrue(partner.vies_checked_on)
        self.assertTrue(partner.vies_is_eu)
        checks = self.env["vies.check"].search(
            [("partner_id", "=", partner.id)])
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks.source, "auto")
        self.assertTrue(checks.name.startswith("VIES/"))
        self.assertEqual(checks.vat, "FR23334175221")

    def test_02_invalid_vat(self):
        with patch(PATCH, return_value=INVALID):
            partner = self._partner("FR83123456709")
        self.assertEqual(partner.vies_state, "invalid")
        self.assertEqual(partner.vies_message, "INVALID")
        check = self.env["vies.check"].search(
            [("partner_id", "=", partner.id)], limit=1)
        self.assertEqual(check.state, "invalid")

    def test_03_service_unavailable(self):
        with patch(PATCH, side_effect=Exception("VIES down")):
            partner = self._partner("FR23334175221")
        self.assertEqual(partner.vies_state, "unavailable")
        self.assertIn("VIES down", partner.vies_message)
        check = self.env["vies.check"].search(
            [("partner_id", "=", partner.id)], limit=1)
        self.assertEqual(check.state, "unavailable")

    def test_04_no_vat_no_check(self):
        partner = self.env["res.partner"].create({"name": "No VAT"})
        self.assertEqual(partner.vies_state, "not_checked")
        self.assertFalse(partner.vies_checked_on)
        self.assertFalse(self.env["vies.check"].search(
            [("partner_id", "=", partner.id)]))

    def test_05_manual_recheck(self):
        with patch(PATCH, return_value=INVALID):
            partner = self._partner("FR23334175221")
        self.assertEqual(partner.vies_state, "invalid")
        with patch(PATCH, return_value=VALID):
            partner.action_vies_check()
        self.assertEqual(partner.vies_state, "valid")
        self.assertEqual(partner.vies_trader_name, "ACME FRANCE")
        checks = self.env["vies.check"].search(
            [("partner_id", "=", partner.id)])
        self.assertEqual(len(checks), 2)
        self.assertIn("manual", checks.mapped("source"))

    def test_06_batch_wizard(self):
        with patch(PATCH, side_effect=Exception("timeout")):
            partners = self.env["res.partner"]
            for index, vat in enumerate(
                    ("FR10123456717", "FR34123456725", "FR58123456733")):
                partners |= self._partner(
                    vat, name="Batch %s" % index)
        self.assertTrue(all(p.vies_state == "unavailable" for p in partners))
        with patch(PATCH, return_value=VALID):
            wizard = self.env["vies.batch.wizard"].create({
                "partner_ids": [(6, 0, partners.ids)],
            })
            wizard.action_run()
        self.assertEqual(wizard.checked_count, 3)
        self.assertEqual(wizard.valid_count, 3)
        self.assertEqual(wizard.invalid_count, 0)
        self.assertTrue(all(p.vies_state == "valid" for p in partners))

    def test_07_cron_recheck(self):
        with patch(PATCH, return_value=VALID):
            partner = self._partner("FR23334175221")
        old = fields.Datetime.now() - timedelta(days=90)
        partner.write({"vies_checked_on": old})
        before = self.env["vies.check"].search_count(
            [("partner_id", "=", partner.id)])
        with patch(PATCH, return_value=VALID):
            self.env["res.partner"]._cron_recheck()
        after = self.env["vies.check"].search_count(
            [("partner_id", "=", partner.id)])
        self.assertEqual(after, before + 1)
        self.assertGreater(partner.vies_checked_on, old)

    def test_08_non_eu_not_checked(self):
        with patch(PATCH) as mocked:
            partner = self._partner("US123456789", country=self.usa)
        self.assertFalse(partner.vies_is_eu)
        self.assertEqual(partner.vies_state, "not_checked")
        mocked.assert_not_called()

    def test_09_manual_check_without_vat(self):
        partner = self.env["res.partner"].create({"name": "Empty VAT"})
        with self.assertRaises(Exception):
            partner.action_vies_check()

    def test_10_change_vat_rechecks(self):
        with patch(PATCH, return_value=VALID):
            partner = self._partner("FR23334175221")
        with patch(PATCH, return_value=INVALID):
            partner.vat = "FR83123456709"
        self.assertEqual(partner.vies_state, "invalid")
        checks = self.env["vies.check"].search(
            [("partner_id", "=", partner.id)])
        self.assertEqual(len(checks), 2)
