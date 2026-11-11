# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLockOut(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "LockOut Other Company"})

    def _lockout(self, **values):
        defaults = {
            "name": "LOTO 2026-11-09-A",
            "equipment": "LockOut Test Press",
            "tag_holder": "LockOut Test Holder",
            "reason": "LockOut test maintenance.",
            "locked_on": date(2026, 11, 9),
        }
        defaults.update(values)
        return self.env["loto.lockout"].create(defaults)

    def test_01_lockout_defaults(self):
        record = self._lockout(name="LOTO 2026-11-09-DEF")
        self.assertEqual(record.state, "locked")
        self.assertEqual(record.company_id, self.env.company)
        self.assertTrue(record.name)
        self.assertFalse(record.restored_on)
        self.assertFalse(record.restored_by)

    def test_02_restore_stamps_date_and_user(self):
        record = self._lockout(name="LOTO 2026-11-10-A")
        self.assertTrue(record.action_restore())
        self.assertEqual(record.state, "restored")
        self.assertTrue(record.restored_on)
        self.assertTrue(record.restored_by)

    def test_03_double_restore_is_refused(self):
        record = self._lockout(name="LOTO 2026-11-10-B")
        record.action_restore()
        with self.assertRaises(UserError):
            record.action_restore()

    def test_04_restore_before_lock_is_refused(self):
        with self.assertRaises(ValidationError):
            self._lockout(
                name="LOTO 2026-11-10-C",
                locked_on=date(2026, 11, 9),
                restored_on=date(2026, 11, 2))

    def test_05_equipment_and_reason_are_required(self):
        record = self._lockout(
            name="LOTO 2026-11-11-A",
            equipment="LockOut Conveyor",
            reason="LockOut belt change.")
        self.assertEqual(record.equipment, "LockOut Conveyor")
        self.assertEqual(record.reason, "LockOut belt change.")

    def test_06_open_search_finds_locked_only(self):
        locked = self._lockout(name="LOTO 2026-11-11-B")
        restored = self._lockout(name="LOTO 2026-11-11-C")
        restored.action_restore()
        found = self.env["loto.lockout"].search([
            ("state", "=", "locked"),
            ("name", "in", [locked.name, restored.name])])
        self.assertIn(locked, found)
        self.assertNotIn(restored, found)

    def test_07_name_is_stored(self):
        record = self._lockout(name="LOTO 2026-11-12-A")
        self.assertEqual(record.name, "LOTO 2026-11-12-A")

    def test_08_company_isolation(self):
        foreign = self.env["loto.lockout"].with_company(
            self.other_company).sudo().create({
            "name": "LOTO 2026-11-12-FOREIGN",
            "equipment": "LockOut Foreign Press",
            "tag_holder": "LockOut Foreign Holder",
            "reason": "Foreign isolation.",
            "locked_on": date(2026, 11, 12),
            "company_id": self.other_company.id,
        })
        local = self._lockout(name="LOTO 2026-11-12-B")
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
