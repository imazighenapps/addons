# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPhotoGuard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "PhotoGuard Other Company"})

    def _audit(self, **values):
        defaults = {
            "name": "PhotoGuard Audit 2026-12",
            "area": "PhotoGuard Web Catalog",
            "owner_name": "PhotoGuard Owner A",
            "due_date": date(2026, 12, 10),
        }
        defaults.update(values)
        return self.env["photo.audit"].create(defaults)

    def _issue(self, audit, **values):
        defaults = {
            "audit_id": audit.id,
            "product_name": "PhotoGuard Product A",
            "issue_type": "missing",
        }
        defaults.update(values)
        return self.env["photo.issue"].create(defaults)

    def test_01_audit_defaults(self):
        audit = self._audit()
        self.assertEqual(audit.state, "draft")
        self.assertEqual(audit.company_id, self.env.company)
        self.assertEqual(audit.issue_count, 0)
        self.assertEqual(audit.quality_score, 0.0)

    def test_02_issue_fix_updates_stats(self):
        audit = self._audit()
        issue = self._issue(audit)
        self.assertEqual(issue.state, "open")
        self.assertTrue(issue.action_fix())
        self.assertEqual(issue.state, "fixed")
        self.assertTrue(issue.fixed_on)
        audit.invalidate_recordset()
        self.assertEqual(audit.issue_count, 1)
        self.assertEqual(audit.open_issue_count, 0)
        self.assertEqual(audit.fixed_issue_count, 1)
        self.assertEqual(audit.quality_score, 100.0)

    def test_03_start_and_done_workflow(self):
        audit = self._audit()
        self._issue(audit)
        self.assertTrue(audit.action_start())
        self.assertEqual(audit.state, "in_progress")
        audit.issue_ids.action_fix()
        self.assertTrue(audit.action_done())
        self.assertEqual(audit.state, "done")

    def test_04_start_without_issues_is_refused(self):
        audit = self._audit()
        with self.assertRaises(UserError):
            audit.action_start()

    def test_05_done_requires_no_open_issues(self):
        audit = self._audit()
        self._issue(audit)
        audit.action_start()
        with self.assertRaises(UserError):
            audit.action_done()

    def test_06_fix_twice_is_refused(self):
        audit = self._audit()
        issue = self._issue(audit)
        issue.action_fix()
        with self.assertRaises(UserError):
            issue.action_fix()

    def test_07_quality_score_with_mixed_issues(self):
        audit = self._audit(name="PhotoGuard Audit 2027-01",
                            due_date=date(2027, 1, 15))
        i1 = self._issue(audit, product_name="PhotoGuard Product B")
        self._issue(audit, product_name="PhotoGuard Product C",
                    issue_type="weak")
        i1.action_fix()
        audit.invalidate_recordset()
        self.assertEqual(audit.issue_count, 2)
        self.assertEqual(audit.fixed_issue_count, 1)
        self.assertEqual(audit.open_issue_count, 1)
        self.assertEqual(audit.quality_score, 50.0)

    def test_08_state_transitions_are_guarded(self):
        audit = self._audit(name="PhotoGuard Audit 2027-02",
                            due_date=date(2027, 2, 20))
        with self.assertRaises(UserError):
            audit.action_done()
        self._issue(audit, product_name="PhotoGuard Product D",
                    issue_type="outdated")
        audit.action_start()
        with self.assertRaises(UserError):
            audit.action_start()

    def test_09_company_isolation(self):
        foreign = self.env["photo.audit"].with_company(
            self.other_company).sudo().create({
            "name": "PhotoGuard Foreign Audit",
            "area": "Foreign Catalog",
            "owner_name": "PhotoGuard Foreign Owner",
            "due_date": date(2027, 3, 5),
            "company_id": self.other_company.id,
        })
        local = self._audit(name="PhotoGuard Local Audit 2027-03",
                            due_date=date(2027, 3, 5))
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertEqual(local.company_id, self.env.company)
        self.assertNotEqual(foreign.company_id, local.company_id)
