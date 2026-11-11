# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestQuarantineDesk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create({"name": "QuarantineDesk Other Company"})

    def _make(self, **vals):
        data = {
            "name": "QD-TEST-001",
            "product_name": "QuarantineDesk Test Product",
            "lot_name": "LOT-QD-01",
            "quantity": 10.0,
            "location_name": "Hold Zone A",
            "reason": "damage",
            "quarantined_on": "2026-02-10",
        }
        data.update(vals)
        return self.env["quarantine.case"].create(data)

    def test_01_defaults(self):
        rec = self._make(name="QD-DEF-2026")
        self.assertEqual(rec.state, "quarantine")
        self.assertEqual(rec.company_id, self.env.company)
        self.assertFalse(rec.decision_date)
        self.assertTrue(rec.active)

    def test_02_release_workflow(self):
        rec = self._make(name="QD-REL-2026", quarantined_on="2026-03-01")
        rec.action_release()
        self.assertEqual(rec.state, "released")
        self.assertTrue(rec.decision_date)

    def test_03_return_and_scrap(self):
        ret = self._make(name="QD-RET-2026", quarantined_on="2026-03-02", lot_name="LOT-QD-RET")
        ret.action_return()
        self.assertEqual(ret.state, "returned")
        scr = self._make(name="QD-SCR-2026", quarantined_on="2026-03-03", lot_name="LOT-QD-SCR")
        scr.action_scrap()
        self.assertEqual(scr.state, "scrapped")

    def test_04_reopen(self):
        rec = self._make(name="QD-REO-2026", quarantined_on="2026-03-04")
        rec.action_release()
        rec.action_reopen()
        self.assertEqual(rec.state, "quarantine")
        self.assertFalse(rec.decision_date)

    def test_05_invalid_transitions(self):
        rec = self._make(name="QD-INV-2026", quarantined_on="2026-04-01")
        with self.assertRaises(UserError):
            rec.action_reopen()
        rec.action_release()
        with self.assertRaises(UserError):
            rec.action_release()

    def test_06_quantity_constraint(self):
        with self.assertRaises(ValidationError):
            self._make(name="QD-QTY-2026", quarantined_on="2026-05-01", quantity=0.0)

    def test_07_decision_date_constraint(self):
        with self.assertRaises(ValidationError):
            self._make(name="QD-DATE-2026", quarantined_on="2026-06-10", decision_date="2026-06-01")

    def test_08_search_filters(self):
        self._make(name="QD-SRCH-A-2026", quarantined_on="2026-07-01", reason="label_issue")
        self._make(name="QD-SRCH-B-2026", quarantined_on="2026-07-02", reason="label_issue")
        recs = self.env["quarantine.case"].search([("name", "in", ["QD-SRCH-A-2026", "QD-SRCH-B-2026"])])
        self.assertEqual(len(recs), 2)

    def test_09_multi_company_isolation(self):
        own = self._make(name="QD-MC-OWN-2026", quarantined_on="2026-08-01")
        foreign = self.env["quarantine.case"].with_company(self.other_company).create({
            "name": "QD-MC-OTH-2026",
            "product_name": "QuarantineDesk Foreign Product",
            "lot_name": "LOT-QD-F",
            "quantity": 2.0,
            "location_name": "Hold Zone Z",
            "reason": "quality",
            "quarantined_on": "2026-08-02",
            "company_id": self.other_company.id,
        })
        self.assertEqual(own.company_id, self.env.company)
        self.assertEqual(foreign.company_id, self.other_company)
        self.assertNotEqual(own.company_id, foreign.company_id)
        self.assertEqual(foreign.state, "quarantine")
