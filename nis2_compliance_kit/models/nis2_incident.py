# -*- coding: utf-8 -*-
import hashlib
from odoo import api, fields, models, _


class Nis2Incident(models.Model):
    _name = "nis2.incident"
    _description = "NIS2 Security Incident"
    _inherit = ["mail.thread"]
    _order = "knowledge_datetime desc"

    name = fields.Char(default="/", readonly=True, copy=False)
    title = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    detection_datetime = fields.Datetime(string="Detected On")
    knowledge_datetime = fields.Datetime(
        string="Known Since",
        required=True,
        help="Moment the incident became known: this starts the 24h / 72h / 1-month clocks.",
    )
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        default="medium",
        tracking=True,
    )
    significant = fields.Boolean(string="Significant Incident", tracking=True)
    significance_note = fields.Text(string="Significance Justification")
    malicious_suspect = fields.Boolean(string="Malicious Action Suspected")
    cross_border = fields.Boolean(string="Cross-Border Impact")
    state = fields.Selection(
        [
            ("detected", "Detected"),
            ("triage", "Triage"),
            ("analysis", "Significance Analysis"),
            ("reportable", "Reportable"),
            ("notreportable", "Not Reportable"),
            ("early", "Early Warning Sent"),
            ("notified", "Notified (72h)"),
            ("interim", "Interim Report"),
            ("final", "Final Report"),
            ("closed", "Closed"),
        ],
        default="detected",
        tracking=True,
    )
    early_deadline = fields.Datetime(compute="_compute_deadlines", store=True)
    notify_deadline = fields.Datetime(compute="_compute_deadlines", store=True)
    final_deadline = fields.Datetime(compute="_compute_deadlines", store=True)
    sla_status = fields.Selection(
        [("ok", "On Time"), ("risk", "At Risk"), ("breached", "Breached")],
        compute="_compute_sla",
    )
    report_ids = fields.One2many("nis2.incident.report", "incident_id", string="Reports")
    asset_ids = fields.Many2many("nis2.asset", string="Impacted Assets")
    description = fields.Text()

    @api.depends("knowledge_datetime")
    def _compute_deadlines(self):
        from datetime import timedelta
        for rec in self:
            base = rec.knowledge_datetime
            rec.early_deadline = base + timedelta(hours=24) if base else False
            rec.notify_deadline = base + timedelta(hours=72) if base else False
            rec.final_deadline = base + timedelta(days=30) if base else False

    @api.depends("state", "early_deadline", "notify_deadline", "final_deadline")
    def _compute_sla(self):
        from datetime import timedelta
        now = fields.Datetime.now()
        for rec in self:
            if rec.state in ("closed", "notreportable"):
                rec.sla_status = "ok"
                continue
            target = {"detected": rec.early_deadline, "triage": rec.early_deadline,
                      "analysis": rec.early_deadline, "reportable": rec.notify_deadline,
                      "early": rec.notify_deadline, "notified": rec.final_deadline,
                      "interim": rec.final_deadline, "final": rec.final_deadline}.get(rec.state)
            if not target:
                rec.sla_status = "ok"
            elif now > target:
                rec.sla_status = "breached"
            elif now + timedelta(hours=6) > target:
                rec.sla_status = "risk"
            else:
                rec.sla_status = "ok"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("nis2.incident") or "/"
        return super().create(vals_list)

    def _advance(self, target, note):
        self.write({"state": target})
        for rec in self:
            rec.message_post(body=note)

    def action_triage(self):
        self._advance("triage", _("Incident triage started."))

    def action_analyze(self):
        self._advance("analysis", _("Significance analysis started."))

    def action_mark_reportable(self):
        self._advance("reportable", _("Incident qualified as significant and reportable."))

    def action_mark_not_reportable(self):
        self._advance("notreportable", _("Incident qualified as not significant."))

    def action_early_sent(self):
        self._advance("early", _("Early warning sent within 24h."))

    def action_notified(self):
        self._advance("notified", _("Notification sent within 72h."))

    def action_interim(self):
        self._advance("interim", _("Interim report submitted."))

    def action_final(self):
        self._advance("final", _("Final report submitted."))

    def action_close(self):
        self._advance("closed", _("Incident closed."))


class Nis2IncidentReport(models.Model):
    _name = "nis2.incident.report"
    _description = "NIS2 Incident Report"

    incident_id = fields.Many2one("nis2.incident", required=True, ondelete="cascade")
    kind = fields.Selection(
        [
            ("early", "Early Warning (24h)"),
            ("notification", "Notification (72h)"),
            ("interim", "Interim Report"),
            ("final", "Final Report (1 month)"),
        ],
        required=True,
    )
    submitted_at = fields.Datetime(default=fields.Datetime.now)
    content = fields.Text(required=True)
    attachment_id = fields.Many2one("ir.attachment", string="Attachment")
    checksum = fields.Char(compute="_compute_checksum", store=True)

    @api.depends("content")
    def _compute_checksum(self):
        for rec in self:
            rec.checksum = hashlib.sha256((rec.content or "").encode("utf-8")).hexdigest()
