# -*- coding: utf-8 -*-
import hashlib
from datetime import timedelta
from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNis2(TransactionCase):
    def test_01_seed_data(self):
        sectors = self.env["nis2.sector"].search([])
        self.assertEqual(len(sectors), 18)
        self.assertEqual(len(sectors.filtered(lambda s: s.annex == "I")), 11)
        self.assertEqual(len(sectors.filtered(lambda s: s.annex == "II")), 7)
        controls = self.env["nis2.control"].search([])
        self.assertEqual(len(controls), 10)

    def test_02_profile_candidacy(self):
        energy = self.env.ref("nis2_compliance_kit.sector_energy")
        big = self.env["nis2.profile"].create({
            "name": "Big Energy Co", "employees": 1200, "turnover": 200.0,
            "balance_sheet": 150.0, "sector_ids": [(6, 0, energy.ids)],
        })
        big.action_suggest_candidacy()
        self.assertEqual(big.candidacy, "essential")
        small = self.env["nis2.profile"].create({
            "name": "Tiny Shop", "employees": 5, "turnover": 1.0, "balance_sheet": 1.0,
        })
        small.action_suggest_candidacy()
        self.assertEqual(small.candidacy, "out")

    def test_03_risk_scores(self):
        risk = self.env["nis2.risk"].create({
            "name": "Ransomware on ERP", "likelihood": "3", "impact": "4",
            "residual_likelihood": "2", "residual_impact": "2",
        })
        self.assertEqual(risk.inherent, 12)
        self.assertEqual(risk.residual, 4)

    def test_04_incident_workflow(self):
        known = fields.Datetime.now() - timedelta(hours=30)
        inc = self.env["nis2.incident"].create({
            "title": "Phishing wave", "knowledge_datetime": known,
            "detection_datetime": known, "severity": "high",
        })
        self.assertTrue(inc.name.startswith("NIS2-INC-"))
        self.assertEqual(inc.early_deadline, known + timedelta(hours=24))
        self.assertEqual(inc.notify_deadline, known + timedelta(hours=72))
        self.assertEqual(inc.final_deadline, known + timedelta(days=30))
        inc.action_triage()
        inc.action_analyze()
        inc.action_mark_reportable()
        self.assertEqual(inc.state, "reportable")
        inc.action_early_sent()
        self.assertEqual(inc.state, "early")
        rep = self.env["nis2.incident.report"].create({
            "incident_id": inc.id, "kind": "early", "content": "Warned CSIRT.",
        })
        self.assertEqual(rep.checksum, hashlib.sha256(b"Warned CSIRT.").hexdigest())
        # notified 30h after detection, well inside the 72h deadline
        self.assertEqual(inc.sla_status, "ok")
        # age the incident past its notification deadline: now it must
        # actually be flagged as breached
        old = fields.Datetime.now() - timedelta(days=10)
        inc.write({"detection_datetime": old, "knowledge_datetime": old})
        inc.action_early_sent()
        self.assertEqual(inc.sla_status, "breached")

    def test_05_supplier_expiry(self):
        partner = self.env["res.partner"].create({"name": "Cloud Hoster"})
        sup = self.env["nis2.supplier"].create({
            "name": "Hoster review", "partner_id": partner.id,
            "criticality": "critical",
            "expiry_date": fields.Date.today() - timedelta(days=1),
        })
        self.assertTrue(sup.expired)
        self.env["nis2.supplier"]._cron_flag_expired()
        self.assertEqual(sup.state, "expired")

    def test_06_control_review(self):
        ctrl = self.env["nis2.control"].search([("code", "=", "a")], limit=1)
        ctrl.write({"review_frequency": "quarterly"})
        ctrl.action_schedule_review()
        self.assertTrue(ctrl.next_review)
        self.assertGreater(ctrl.next_review, fields.Date.today())
