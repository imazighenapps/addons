# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSiteAudit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({
            "name": "SiteAudit Other Company"})
        cls.template = cls.env["size.audit.template"].create({
            "name": "SiteAudit Test Template",
            "line_ids": [
                (0, 0, {"name": "Exits are clear", "points_max": 20.0,
                        "category": "safety"}),
                (0, 0, {"name": "Floors are clean", "points_max": 10.0,
                        "category": "cleanliness"}),
                (0, 0, {"name": "Guards are fitted", "points_max": 10.0,
                        "category": "equipment"}),
            ],
        })

    def _audit(self, **values):
        defaults = {
            "site_name": "SiteAudit Test Site",
            "template_id": self.template.id,
        }
        defaults.update(values)
        return self.env["site.audit"].create(defaults)

    def _lines(self, audit):
        result = {line.name: line for line in audit.line_ids}
        return result

    def test_01_template_lines_are_instantiated(self):
        audit = self._audit()
        self.assertEqual(audit.point_count, 3)
        self.assertEqual(audit.state, "draft")
        self.assertEqual(len(audit.line_ids), 3)
        self.assertTrue(all(not line.scored for line in audit.line_ids))
        self.assertTrue(audit.audit_date)
        self.assertTrue(audit.name.startswith("Site audit "))
        self.assertEqual(audit.auditor_id, self.env.user)
        self.assertEqual(audit.company_id, self.env.company)

    def test_02_score_is_weighted(self):
        audit = self._audit()
        lines = self._lines(audit)
        lines["Exits are clear"].write({"score": 10.0, "scored": True})
        lines["Floors are clean"].write({"score": 10.0, "scored": True})
        lines["Guards are fitted"].write({"score": 10.0, "scored": True})
        audit.invalidate_recordset()
        self.assertEqual(audit.score_pct, round(30.0 / 40.0 * 100.0, 1))

    def test_03_pass_and_fail_thresholds(self):
        audit = self._audit()
        lines = self._lines(audit)
        lines["Exits are clear"].write({"score": 9.0, "scored": True})
        lines["Floors are clean"].write({"score": 0.0, "scored": True})
        lines["Guards are fitted"].write({"score": 6.0, "scored": True})
        audit.invalidate_recordset()
        self.assertEqual(lines["Exits are clear"].state, "failed")
        self.assertEqual(lines["Floors are clean"].state, "failed")
        self.assertEqual(lines["Guards are fitted"].state, "passed")

    def test_04_unscored_lines_block_the_close(self):
        audit = self._audit()
        with self.assertRaises(UserError):
            audit.action_done()
        audit.line_ids.write({"score": 5.0, "scored": True})
        audit.invalidate_recordset()
        self.assertTrue(audit.action_done())
        self.assertEqual(audit.state, "done")

    def test_05_close_twice_and_reopen(self):
        audit = self._audit()
        audit.line_ids.write({"score": 5.0, "scored": True})
        audit.action_done()
        with self.assertRaises(UserError):
            audit.action_done()
        audit.action_reopen()
        self.assertEqual(audit.state, "draft")

    def test_06_scores_are_bounded(self):
        audit = self._audit()
        line = audit.line_ids[0]
        with self.assertRaises(ValidationError):
            line.write({"score": -1.0, "scored": True})
        with self.assertRaises(ValidationError):
            line.write({"score": 25.0, "scored": True})

    def test_07_reset_rebuilds_the_lines(self):
        audit = self._audit()
        audit.line_ids.write({"score": 1.0, "scored": True})
        audit.action_reset()
        self.assertEqual(audit.point_count, 3)
        self.assertTrue(all(not line.scored for line in audit.line_ids))
        self.assertTrue(all(
            line.state == "pending" for line in audit.line_ids))

    def test_08_cancel(self):
        audit = self._audit()
        audit.action_cancel()
        self.assertEqual(audit.state, "cancelled")
        audit.action_reopen()
        self.assertEqual(audit.state, "draft")

    def test_09_company_isolation(self):
        foreign = self.env["site.audit"].sudo().create({
            "site_name": "SiteAudit Test Foreign Site",
            "template_id": self.template.id,
            "company_id": self.other_company.id,
        })
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(foreign.company_id, self.env.company)
        local = self._audit()
        self.assertEqual(local.company_id, self.env.company)
