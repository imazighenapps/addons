# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestKeyBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "KeyBook Other Company"})

    def _key(self, **values):
        defaults = {
            "name": "KEY 2026-11-09-A",
            "label": "KeyBook Test Front Door",
            "key_type": "key",
            "holder": "KeyBook Test Holder",
            "issued_on": date(2026, 11, 9),
        }
        defaults.update(values)
        return self.env["key.item"].create(defaults)

    def test_01_key_defaults(self):
        record = self._key(name="KEY 2026-11-09-DEF")
        self.assertEqual(record.state, "issued")
        self.assertEqual(record.company_id, self.env.company)
        self.assertFalse(record.returned_on)
        self.assertEqual(record.key_type, "key")

    def test_02_return_stamps_date(self):
        record = self._key(name="KEY 2026-11-10-A")
        self.assertTrue(record.action_return())
        self.assertEqual(record.state, "returned")
        self.assertTrue(record.returned_on)

    def test_03_double_return_is_refused(self):
        record = self._key(name="KEY 2026-11-10-B")
        record.action_return()
        with self.assertRaises(UserError):
            record.action_return()

    def test_04_return_before_issue_is_refused(self):
        with self.assertRaises(ValidationError):
            self._key(
                name="KEY 2026-11-10-C",
                issued_on=date(2026, 11, 9),
                returned_on=date(2026, 11, 2))

    def test_05_key_types(self):
        badge = self._key(name="KEY 2026-11-11-A", key_type="badge",
                          label="KeyBook Badge A")
        fob = self._key(name="KEY 2026-11-11-B", key_type="fob",
                        label="KeyBook Fob B")
        self.assertEqual(badge.key_type, "badge")
        self.assertEqual(fob.key_type, "fob")

    def test_06_holder_is_stored(self):
        record = self._key(name="KEY 2026-11-11-C",
                           holder="KeyBook New Holder")
        self.assertEqual(record.holder, "KeyBook New Holder")

    def test_07_missing_search_finds_issued_only(self):
        issued = self._key(name="KEY 2026-11-12-A")
        returned = self._key(name="KEY 2026-11-12-B",
                             label="KeyBook Returned Key")
        returned.action_return()
        found = self.env["key.item"].search([
            ("state", "=", "issued"),
            ("name", "in", [issued.name, returned.name])])
        self.assertIn(issued, found)
        self.assertNotIn(returned, found)

    def test_08_company_isolation(self):
        foreign = self.env["key.item"].with_company(
            self.other_company).sudo().create({
            "name": "KEY 2026-11-12-FOREIGN",
            "label": "Foreign Key",
            "key_type": "key",
            "holder": "Foreign Holder",
            "issued_on": date(2026, 11, 12),
            "company_id": self.other_company.id,
        })
        local = self._key(name="KEY 2026-11-12-C")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
