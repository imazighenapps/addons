# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestForkCheck(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "ForkCheck Other Company"})

    def _check(self, **values):
        defaults = {
            "name": "ForkCheck Daily A",
            "truck_ref": "ForkCheck Truck A",
            "operator_name": "ForkCheck Operator A",
            "check_date": date(2026, 4, 10),
            "company_id": self.env.company.id,
        }
        defaults.update(values)
        return self.env["forklift.check"].create(defaults)

    def _defect(self, check, **values):
        defaults = {
            "name": "ForkCheck Tyre Worn",
            "check_id": check.id,
            "severity": "high",
        }
        defaults.update(values)
        return self.env["forklift.defect"].create(defaults)

    def test_01_check_defaults(self):
        check = self._check()
        self.assertEqual(check.state, "draft")
        self.assertEqual(check.company_id, self.env.company)
        self.assertEqual(check.defect_count, 0)
        self.assertEqual(check.open_defect_count, 0)

    def test_02_validate_ready_when_no_open_defect(self):
        check = self._check()
        self.assertTrue(check.action_validate())
        self.assertEqual(check.state, "ready")

    def test_03_validate_grounded_with_open_defect(self):
        check = self._check(name="ForkCheck Daily B")
        self._defect(check)
        self.assertTrue(check.action_validate())
        self.assertEqual(check.state, "grounded")

    def test_04_double_validate_is_refused(self):
        check = self._check(name="ForkCheck Daily C")
        check.action_validate()
        with self.assertRaises(ValidationError):
            check.action_validate()

    def test_05_reopen_and_reopen_draft_is_refused(self):
        check = self._check(name="ForkCheck Daily D")
        check.action_validate()
        self.assertTrue(check.action_reopen())
        self.assertEqual(check.state, "draft")
        with self.assertRaises(ValidationError):
            check.action_reopen()

    def test_06_defect_signoff(self):
        check = self._check(name="ForkCheck Daily E")
        defect = self._defect(check, name="ForkCheck Brake Weak")
        self.assertTrue(defect.action_signoff())
        self.assertEqual(defect.state, "fixed")
        self.assertTrue(defect.signed_off_on)

    def test_07_double_signoff_is_refused(self):
        check = self._check(name="ForkCheck Daily F")
        defect = self._defect(check, name="ForkCheck Leak")
        defect.action_signoff()
        with self.assertRaises(ValidationError):
            defect.action_signoff()

    def test_08_fixed_defect_requires_signoff_date(self):
        check = self._check(name="ForkCheck Daily G")
        with self.assertRaises(ValidationError):
            self.env["forklift.defect"].create({
                "name": "ForkCheck Fork Crack",
                "check_id": check.id,
                "state": "fixed",
            })

    def test_09_open_defect_counter(self):
        check = self._check(name="ForkCheck Daily H")
        open_defect = self._defect(check, name="ForkCheck Horn")
        fixed = self._defect(check, name="ForkCheck Light")
        fixed.action_signoff()
        check.invalidate_recordset()
        self.assertEqual(check.defect_count, 2)
        self.assertEqual(check.open_defect_count, 1)
        self.assertEqual(open_defect.state, "open")

    def test_10_company_isolation(self):
        foreign = self.env["forklift.check"].with_company(
            self.other_company).create({
            "name": "ForkCheck Foreign Daily",
            "truck_ref": "ForkCheck Truck Z",
            "operator_name": "ForkCheck Operator Z",
            "check_date": date(2026, 4, 10),
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        local = self._check(name="ForkCheck Local Daily")
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(local.company_id, foreign.company_id)
