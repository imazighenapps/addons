# -*- coding: utf-8 -*-
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGdpr(TransactionCase):
    def test_01_activity_lifecycle(self):
        act = self.env["gdpr.activity"].create({
            "name": "CRM Prospection", "role": "controller",
            "purposes": "<p>Prospecting</p>", "legal_basis": "legitimate",
            "owner_id": self.env.uid,
        })
        self.assertEqual(act.state, "draft")
        self.assertEqual(act.version, 1)

    def test_02_dsar_deadline(self):
        dsar = self.env["gdpr.dsar"].create({
            "requester_name": "John Doe", "requester_email": "john@demo.test",
            "right": "access", "receipt_date": fields.Date.today(),
        })
        self.assertTrue(dsar.name.startswith("DSAR-"))
        self.assertEqual(dsar.deadline, fields.Date.today() + relativedelta(months=1))
        dsar.action_answer()
        self.assertEqual(dsar.state, "answered")

    def test_03_dsar_refuse_requires_reason(self):
        dsar = self.env["gdpr.dsar"].create({
            "requester_name": "Jane", "right": "erasure",
            "receipt_date": fields.Date.today(),
        })
        with self.assertRaises(UserError):
            dsar.action_refuse()
        dsar.refusal_reason = "Manifestly unfounded, see case file."
        dsar.action_refuse()
        self.assertEqual(dsar.state, "refused")

    def test_04_dpia_screening(self):
        dpia = self.env["gdpr.dpia"].create({
            "name": "AI Scoring DPIA", "crit_auto": True, "crit_scale": True,
        })
        self.assertEqual(dpia.score, 2)
        self.assertTrue(dpia.need_dpia)
        with self.assertRaises(UserError):
            dpia.write({"residual": "high"})
            dpia.action_decide()
        dpia.write({"residual": "medium", "consultation": False})
        dpia.action_decide()
        self.assertEqual(dpia.state, "decided")

    def test_05_breach_deadline(self):
        aware = fields.Datetime.now()
        breach = self.env["gdpr.breach"].create({
            "awareness_date": aware, "nature": "confidentiality", "risk": "high",
        })
        self.assertTrue(breach.name.startswith("BREACH-"))
        self.assertEqual(breach.notify_deadline, aware + timedelta(hours=72))
        breach.action_assess()
        breach.action_notify()
        self.assertTrue(breach.notified_date)
        self.assertEqual(breach.state, "notified")

    def test_06_anonym_log(self):
        log = self.env["gdpr.anonymization.log"].create({
            "model_name": "res.partner", "record_ref": "Partner #42",
            "fields_list": "name, email, phone",
        })
        self.assertTrue(log.name.startswith("ANON-"))
