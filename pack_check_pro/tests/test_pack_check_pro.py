# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPackCheck(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({"name": "PackCheck Other Company"})

    def _make(self, **vals):
        data = {
            "name": "PC-TEST-001",
            "reference": "SHIP-PC-001",
            "packer": "Alice",
            "checker": "Bob",
            "check_date": "2026-02-15",
            "expected_weight": 10.0,
            "actual_weight": 10.0,
            "expected_count": 5,
            "actual_count": 5,
        }
        data.update(vals)
        return self.env["pack.check"].create(data)

    def test_01_defaults(self):
        rec = self._make(name="PC-DEF-2026")
        self.assertEqual(rec.state, "draft")
        self.assertEqual(rec.company_id, self.env.company)
        self.assertFalse(rec.decision_date)
        self.assertTrue(rec.active)

    def test_02_compute_pass(self):
        rec = self._make(name="PC-PASS-2026")
        self.assertEqual(rec.result, "pass")
        self.assertEqual(rec.weight_variance, 0.0)
        self.assertEqual(rec.count_variance, 0)

    def test_03_compute_fail(self):
        rec = self._make(name="PC-FAIL-2026", actual_weight=9.5, actual_count=4)
        self.assertEqual(rec.result, "fail")
        self.assertAlmostEqual(rec.weight_variance, -0.5, places=6)
        self.assertEqual(rec.count_variance, -1)

    def test_04_workflow_approve(self):
        rec = self._make(name="PC-WF-A-2026", check_date="2026-03-01")
        rec.action_check()
        self.assertEqual(rec.state, "checked")
        rec.action_approve()
        self.assertEqual(rec.state, "approved")
        self.assertTrue(rec.decision_date)

    def test_05_workflow_reject_and_reset(self):
        rec = self._make(name="PC-WF-R-2026", check_date="2026-03-02", actual_count=4)
        rec.action_check()
        rec.action_reject()
        self.assertEqual(rec.state, "rejected")
        self.assertTrue(rec.decision_date)
        rec.action_reset()
        self.assertEqual(rec.state, "draft")
        self.assertFalse(rec.decision_date)

    def test_06_invalid_transitions(self):
        rec = self._make(name="PC-INV-2026", check_date="2026-04-01")
        with self.assertRaises(UserError):
            rec.action_approve()
        with self.assertRaises(UserError):
            rec.action_reset()
        rec.action_check()
        with self.assertRaises(UserError):
            rec.action_check()

    def test_07_constraints(self):
        with self.assertRaises(ValidationError):
            self._make(name="PC-WNEG-2026", check_date="2026-05-01", expected_weight=-1.0)
        with self.assertRaises(ValidationError):
            self._make(name="PC-CNEG-2026", check_date="2026-05-02", expected_count=-1)

    def test_08_search_counts(self):
        self._make(name="PC-SRCH-A-2026", check_date="2026-06-01")
        self._make(name="PC-SRCH-B-2026", check_date="2026-06-02", actual_count=3)
        recs = self.env["pack.check"].search([("name", "in", ["PC-SRCH-A-2026", "PC-SRCH-B-2026"])])
        self.assertEqual(len(recs), 2)

    def test_09_multi_company_isolation(self):
        own = self._make(name="PC-MC-OWN-2026", check_date="2026-07-01")
        foreign = self.env["pack.check"].with_company(self.other_company).create({
            "name": "PC-MC-OTH-2026",
            "reference": "SHIP-PC-F",
            "check_date": "2026-07-02",
            "expected_weight": 8.0,
            "actual_weight": 8.0,
            "expected_count": 2,
            "actual_count": 2,
            "company_id": self.other_company.id,
        })
        self.assertEqual(own.company_id, self.env.company)
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(own.company_id, foreign.company_id)
        self.assertEqual(foreign.result, "pass")
