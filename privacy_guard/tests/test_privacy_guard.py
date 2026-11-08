# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPrivacyGuard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create({
            "name": "PrivacyGuard Test Subject",
            "email": "subject@example.com",
            "comment": "Sensitive note",
        })

    def _backdate(self, record, days=400):
        """Make a res.partner look old.

        create_date is written by the ORM and cannot be assigned: a direct
        SQL update followed by a cache invalidation is the only hermetic way
        to simulate an old record in a test. The transaction is rolled back,
        so no other test is affected.
        """
        create_date = fields.Datetime.now() - timedelta(days=days)
        self.env.cr.execute(
            "UPDATE res_partner SET create_date = %s WHERE id = %s",
            (create_date, record.id))
        record.invalidate_recordset(["create_date"])
        return record

    def _text(self, value):
        """An html field comes back wrapped in a paragraph."""
        text = str(value or "")
        return text.replace("<p>", "").replace("</p>", "")

    def _rule(self, **kwargs):
        type(self)._rule_seq = getattr(type(self), "_rule_seq", 0) + 1
        values = {
            "name": "PrivacyGuard Rule %s" % type(self)._rule_seq,
            "model_name": "res.partner",
            "date_field": "create_date",
            "retention_days": 365,
            "action": "anonymize",
            "field_list": "comment",
        }
        values.update(kwargs)
        return self.env["privacy.rule"].create(values)

    def test_01_rule_detects_expired_record(self):
        partner = self.env["res.partner"].create({
            "name": "PrivacyGuard Old Contact"})
        self._backdate(partner, 400)
        rule = self._rule()
        expired = rule._get_expired_records()
        self.assertIn(partner, expired)
        self.assertEqual(rule._get_expired_records()._name, "res.partner")

    def test_02_recent_record_is_not_expired(self):
        partner = self.env["res.partner"].create({
            "name": "PrivacyGuard New Contact"})
        rule = self._rule()
        self.assertNotIn(partner, rule._get_expired_records())
        with self.assertRaises(ValidationError):
            self._rule(model_name="privacy.unknown.model")
        with self.assertRaises(ValidationError):
            self._rule(date_field="name")
        with self.assertRaises(ValidationError):
            self._rule(retention_days=0)

    def test_03_anonymize_masks_listed_fields(self):
        partner = self.env["res.partner"].create({
            "name": "PrivacyGuard Masked Contact",
            "email": "mask@example.com",
            "comment": "Sensitive note",
        })
        rule = self._rule(field_list="email\ncomment", mask_char="#")
        masked = rule._anonymize_record(partner)
        self.assertEqual(sorted(masked), ["comment", "email"])
        self.assertEqual(partner.email, "######")
        self.assertEqual(self._text(partner.comment), "######")
        self.assertEqual(partner.name, "PrivacyGuard Masked Contact")

    def test_04_archive_deactivates_records(self):
        partner = self.env["res.partner"].create({
            "name": "PrivacyGuard Archived Contact"})
        request = self.env["privacy.request"].create({
            "name": "PrivacyGuard Old Request",
            "partner_id": partner.id,
            "request_type": "access",
            "date_request": date(2020, 1, 1),
        })
        self.assertTrue(request.active)
        rule = self._rule(
            model_name="privacy.request", date_field="date_request",
            retention_days=365, action="archive", field_list="")
        scan = self.env["privacy.scan"].create({
            "rule_ids": [(6, 0, rule.ids)],
            "dry_run": False,
        })
        self.assertTrue(scan.action_scan())
        self.assertFalse(request.active)

    def test_05_delete_never_removes_a_partner(self):
        partner = self.env["res.partner"].create({
            "name": "PrivacyGuard Erasure Contact",
            "comment": "Erase me",
        })
        self._backdate(partner, 400)
        rule = self._rule(action="delete", field_list="comment")
        scan = self.env["privacy.scan"].create({
            "rule_ids": [(6, 0, rule.ids)],
            "dry_run": False,
        })
        self.assertTrue(scan.action_scan())
        self.assertTrue(partner.exists())
        self.assertEqual(self._text(partner.comment), "******")
        self.assertEqual(
            self.env["privacy.rule"].browse(rule.id).model_name, "res.partner")

    def test_06_request_anonymize_partner(self):
        partner = self.env["res.partner"].create({
            "name": "PrivacyGuard Data Subject",
            "email": "subject2@example.com",
            "comment": "Please erase me",
        })
        rule = self._rule(field_list="email\ncomment")
        request = self.env["privacy.request"].create({
            "name": "PrivacyGuard Erasure",
            "partner_id": partner.id,
            "request_type": "erasure",
            "date_request": date(2099, 1, 15),
            "rule_ids": [(6, 0, rule.ids)],
        })
        self.assertEqual(request.date_deadline, date(2099, 2, 14))
        self.assertTrue(request.action_start())
        self.assertEqual(request.state, "in_progress")
        self.assertTrue(request.action_anonymize_partner())
        self.assertEqual(request.state, "done")
        self.assertEqual(partner.email, "******")
        self.assertEqual(self._text(partner.comment), "******")
        self.assertTrue(partner.exists())
        self.assertIn("email", request.resolution_note)
        refused = self.env["privacy.request"].create({
            "name": "PrivacyGuard Refused",
            "partner_id": partner.id,
            "request_type": "access",
            "date_request": date(2099, 3, 1),
        })
        self.assertTrue(refused.action_refuse())
        self.assertEqual(refused.state, "refused")
        with self.assertRaises(UserError):
            refused.action_done()

    def test_07_scan_dry_run_changes_nothing(self):
        partner = self.env["res.partner"].create({
            "name": "PrivacyGuard Dry Contact",
            "comment": "Do not touch",
        })
        self._backdate(partner, 400)
        rule = self._rule(field_list="comment")
        scan = self.env["privacy.scan"].create({
            "rule_ids": [(6, 0, rule.ids)],
            "dry_run": True,
        })
        self.assertTrue(scan.action_scan())
        self.assertEqual(self._text(partner.comment), "Do not touch")
        self.assertTrue(partner.active)
        self.assertTrue(partner.exists())

    def test_08_company_isolation(self):
        other_company = self.env["res.company"].create({
            "name": "PrivacyGuard Other Company"})
        self.env.user.write({"company_ids": [(4, other_company.id)]})
        mine = self.env["privacy.request"].create({
            "name": "PrivacyGuard Request Mine",
            "partner_id": self.partner.id,
            "request_type": "access",
            "date_request": date(2020, 1, 1),
            "company_id": self.company.id,
        })
        theirs = self.env["privacy.request"].create({
            "name": "PrivacyGuard Request Other",
            "partner_id": self.partner.id,
            "request_type": "access",
            "date_request": date(2020, 1, 1),
            "company_id": other_company.id,
        })
        rule = self._rule(
            model_name="privacy.request", date_field="date_request",
            retention_days=30, action="archive", field_list="",
            company_id=self.company.id)
        expired = rule._get_expired_records()
        self.assertIn(mine, expired)
        self.assertNotIn(theirs, expired)
