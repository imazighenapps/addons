from datetime import date as pydate

from odoo import api, fields, models, _

class QmsDashboard(models.Model):
    _name = "qms.dashboard"
    _description = "QMS Executive Dashboard"
    _order = "company_id"

    name = fields.Char(required=True, default="QMS Executive Cockpit")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        check_company=True, index=True, readonly=True,
    )
    refreshed_at = fields.Datetime(readonly=True)

    requirement_total = fields.Integer(readonly=True)
    requirement_supported = fields.Integer(readonly=True)
    requirement_partial = fields.Integer(readonly=True)
    requirement_missing = fields.Integer(readonly=True)
    requirement_coverage = fields.Float(readonly=True, digits=(16, 2))

    valid_evidence_count = fields.Integer(readonly=True)
    expired_evidence_count = fields.Integer(readonly=True)
    published_document_count = fields.Integer(readonly=True)
    overdue_document_review_count = fields.Integer(readonly=True)

    open_ncr_count = fields.Integer(readonly=True)
    major_ncr_count = fields.Integer(readonly=True)
    overdue_capa_count = fields.Integer(readonly=True)
    high_risk_count = fields.Integer(readonly=True)

    training_gap_count = fields.Integer(readonly=True)
    objectives_at_risk_count = fields.Integer(readonly=True)
    open_audit_count = fields.Integer(readonly=True)
    audit_compliance_rate = fields.Float(readonly=True, digits=(16, 2))
    open_complaint_count = fields.Integer(readonly=True)
    breached_complaint_count = fields.Integer(readonly=True)
    overdue_calibration_count = fields.Integer(readonly=True)
    open_improvement_count = fields.Integer(readonly=True)
    open_opportunity_count = fields.Integer(readonly=True)
    compliance_gap_count = fields.Integer(readonly=True)
    cost_of_quality = fields.Monetary(readonly=True, currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", readonly=True)

    readiness_index = fields.Float(readonly=True, digits=(16, 2))
    methodology_note = fields.Text(
        readonly=True,
        default=(
            "Internal readiness index based on requirement coverage, evidence validity, "
            "document review status, CAPA timeliness, residual risk exposure and training status. "
            "It is a management indicator, not an ISO certification score."
        ),
    )

    readiness_band = fields.Selection(
        [
            ("strong", "Strong"),
            ("attention", "Needs Attention"),
            ("gap", "Priority Gaps"),
        ], readonly=True,
    )

    _company_uniq = models.Constraint(
        "UNIQUE(company_id)",
        "Only one dashboard snapshot is kept per company.",
    )

    @api.model
    def _get_or_create_current(self):
        record = self.search([("company_id", "=", self.env.company.id)], limit=1)
        return record or self.create({"company_id": self.env.company.id})

    def _group_counts(self, model_name, domain, field_name):
        result = {}
        for key, count in self.env[model_name]._read_group(domain, [field_name], ["id:count"]):
            if isinstance(key, (list, tuple)):
                key = key[0] if key else False
            elif hasattr(key, "id"):
                key = key.id
            if key:
                result[key] = count
        return result

    def _compute_counts(self):
        self.ensure_one()
        company = self.company_id
        base = [("company_id", "=", company.id)]
        today = fields.Date.context_today(self)

        req = self._group_counts("qms.requirement", base, "compliance_state")
        evidence = self._group_counts("qms.evidence", base, "status")
        documents = self._group_counts("qms.document", base, "state")
        ncrs = self._group_counts("qms.ncr", base, "status")
        ncr_major = self.env["qms.ncr"].search_count(base + [("status", "!=", "closed"), ("severity", "in", ["major", "critical"])])
        overdue_capa = self.env["qms.capa"].search_count(base + [("deadline", "<", today), ("status", "not in", ["effective", "cancelled"])])
        high_risk = self.env["qms.risk"].search_count(base + [("residual_level", "in", ["high", "critical"])])
        training = self._group_counts("qms.training.assignment", base, "state")
        objectives = self._group_counts("qms.objective", base, "status")
        audits = self._group_counts("qms.audit", base, "state")
        complaints = self._group_counts("qms.complaint", base, "state")
        breached_complaints = self.env["qms.complaint"].search_count(base + [("sla_breached", "=", True), ("state", "not in", ["closed", "cancelled"])])
        equipment = self._group_counts("qms.measurement.equipment", base, "state")
        improvements = self._group_counts("qms.improvement", base, "status")
        opportunities = self._group_counts("qms.opportunity", base, "status")
        quality_cost_rows = self.env["qms.quality.cost"]._read_group(base, [], ["amount:sum"])
        cost_of_quality = (quality_cost_rows[0][0] if quality_cost_rows and quality_cost_rows[0][0] else 0.0)

        requirement_total = sum(req.values())
        supported = req.get("supported", 0)
        partial = req.get("partial", 0)
        missing = req.get("missing", 0)
        coverage = supported / requirement_total * 100.0 if requirement_total else 0.0
        closed_audits = self.env["qms.audit"].search(base + [("state", "=", "closed")])
        rates = [audit.compliance_rate for audit in closed_audits if audit.line_count]
        audit_rate = sum(rates) / len(rates) if rates else 0.0

        valid_evidence = evidence.get("valid", 0)
        evidence_total = sum(evidence.values())
        evidence_factor = valid_evidence / evidence_total * 100.0 if evidence_total else 0.0
        open_major_factor = max(0.0, 100.0 - min(ncr_major * 10.0, 100.0))
        capa_factor = max(0.0, 100.0 - min(overdue_capa * 12.5, 100.0))
        risk_factor = max(0.0, 100.0 - min(high_risk * 8.0, 100.0))
        training_gaps = training.get("expired", 0) + training.get("assigned", 0) + training.get("failed", 0)
        training_factor = max(0.0, 100.0 - min(training_gaps * 5.0, 100.0))
        open_complaints = sum(v for k, v in complaints.items() if k not in ("closed", "cancelled"))
        complaint_factor = max(0.0, 100.0 - min(breached_complaints * 10.0, 100.0))
        overdue_calibration = equipment.get("overdue", 0)
        calibration_factor = max(0.0, 100.0 - min(overdue_calibration * 8.0, 100.0))
        readiness = round((coverage * 0.30) + (evidence_factor * 0.12) + (open_major_factor * 0.12) + (capa_factor * 0.12) + (risk_factor * 0.10) + (training_factor * 0.08) + (complaint_factor * 0.08) + (calibration_factor * 0.08), 2)
        band = "strong" if readiness >= 85 else "attention" if readiness >= 70 else "gap"

        return {
            "refreshed_at": fields.Datetime.now(),
            "requirement_total": requirement_total,
            "requirement_supported": supported,
            "requirement_partial": partial,
            "requirement_missing": missing,
            "requirement_coverage": coverage,
            "valid_evidence_count": valid_evidence,
            "expired_evidence_count": evidence.get("expired", 0),
            "published_document_count": documents.get("published", 0),
            "overdue_document_review_count": self.env["qms.document"].search_count(base + [("state", "=", "published"), ("review_date", "<", today)]),
            "open_ncr_count": sum(v for k, v in ncrs.items() if k != "closed"),
            "major_ncr_count": ncr_major,
            "overdue_capa_count": overdue_capa,
            "high_risk_count": high_risk,
            "training_gap_count": training_gaps,
            "objectives_at_risk_count": objectives.get("at_risk", 0) + objectives.get("delayed", 0),
            "open_audit_count": sum(v for k, v in audits.items() if k != "closed"),
            "audit_compliance_rate": audit_rate,
            "open_complaint_count": open_complaints,
            "breached_complaint_count": breached_complaints,
            "overdue_calibration_count": overdue_calibration,
            "open_improvement_count": sum(v for k, v in improvements.items() if k not in ("completed", "standardized", "cancelled")),
            "open_opportunity_count": sum(v for k, v in opportunities.items() if k not in ("completed", "rejected")),
            "compliance_gap_count": missing + partial,
            "cost_of_quality": cost_of_quality,
            "readiness_index": readiness,
            "readiness_band": band,
        }

    def action_refresh(self):
        for record in self:
            record.write(record._compute_counts())
        return True

    @api.model
    def get_dashboard_data(self):
        """Data payload for the OWL cockpit (KPIs + charts)."""
        record = self._get_or_create_current()
        vals = record._compute_counts()
        record.write(vals)
        company = record.company_id
        base = [("company_id", "=", company.id)]
        today = fields.Date.context_today(self)

        months, ncr_trend, audit_trend = self._monthly_trend(base, today)
        ncr_states = ["new", "containment", "analysis", "action", "effectiveness", "closed"]
        ncr_labels = ["New", "Containment", "Analysis", "Action Plan", "Effectiveness", "Closed"]
        ncr_counts = self._group_counts("qms.ncr", base, "status")
        complaint_counts = self._group_counts("qms.complaint", base, "state")
        complaint_labels = {
            "new": "New", "acknowledged": "Acknowledged", "investigating": "Investigating",
            "waiting_customer": "Waiting Customer", "resolved": "Resolved",
            "closed": "Closed", "cancelled": "Cancelled",
        }
        band_labels = {"strong": "Strong", "attention": "Needs Attention", "gap": "Priority Gaps"}
        return {
            "readiness_index": vals["readiness_index"],
            "readiness_band": vals["readiness_band"],
            "readiness_label": band_labels.get(vals["readiness_band"], ""),
            "kpis": {
                "open_ncr": vals["open_ncr_count"],
                "overdue_capa": vals["overdue_capa_count"],
                "open_audits": vals["open_audit_count"],
                "coverage": round(vals["requirement_coverage"], 1),
                "open_complaints": vals["open_complaint_count"],
                "training_gaps": vals["training_gap_count"],
                "overdue_calibration": vals["overdue_calibration_count"],
                "high_risks": vals["high_risk_count"],
            },
            "charts": {
                "coverage": {
                    "labels": ["Supported", "Partial", "Missing"],
                    "data": [vals["requirement_supported"], vals["requirement_partial"], vals["requirement_missing"]],
                },
                "ncr_status": {
                    "labels": ncr_labels,
                    "data": [ncr_counts.get(state, 0) for state in ncr_states],
                },
                "monthly": {"labels": months, "ncr": ncr_trend, "audits": audit_trend},
                "complaints": {
                    "labels": [complaint_labels.get(state, state) for state in sorted(complaint_counts)],
                    "data": [complaint_counts[state] for state in sorted(complaint_counts)],
                },
            },
        }

    @api.model
    def _monthly_trend(self, base_domain, today, months=6):
        """NCR / audit volumes per month for the last N months."""
        labels, ncr_data, audit_data = [], [], []
        year, month = today.year, today.month
        for back in range(months - 1, -1, -1):
            m = month - back
            y = year
            while m <= 0:
                m += 12
                y -= 1
            start = fields.Date.to_string(pydate(y, m, 1))
            if m == 12:
                end = fields.Date.to_string(pydate(y + 1, 1, 1))
            else:
                end = fields.Date.to_string(pydate(y, m + 1, 1))
            period = [("create_date", ">=", start), ("create_date", "<", end)]
            labels.append(pydate(y, m, 1).strftime("%b %y"))
            ncr_data.append(self.env["qms.ncr"].search_count(base_domain + period))
            audit_data.append(self.env["qms.audit"].search_count(base_domain + period))
        return labels, ncr_data, audit_data

    @api.model
    def action_open_dashboard(self):
        record = self._get_or_create_current()
        record.action_refresh()
        return {
            "type": "ir.actions.act_window",
            "name": "QMS Executive Cockpit",
            "res_model": "qms.dashboard",
            "view_mode": "form",
            "res_id": record.id,
            "target": "current",
        }

    def _open_action(self, model, domain=None, name=None):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": name or "QMS",
            "res_model": model,
            "view_mode": "list,form",
            "domain": domain or [("company_id", "=", self.company_id.id)],
            "target": "current",
        }

    def action_open_missing_requirements(self):
        return self._open_action("qms.requirement", [("company_id", "=", self.company_id.id), ("compliance_state", "in", ["missing", "partial"])], "Requirements Needing Evidence")

    def action_open_ncr(self):
        return self._open_action("qms.ncr", [("company_id", "=", self.company_id.id), ("status", "!=", "closed")], "Open NCR")

    def action_open_capa(self):
        return self._open_action("qms.capa", [("company_id", "=", self.company_id.id), ("status", "not in", ["effective", "cancelled"])], "Open CAPA")

    def action_open_risks(self):
        return self._open_action("qms.risk", [("company_id", "=", self.company_id.id), ("residual_level", "in", ["high", "critical"])], "High and Critical Risks")

    def action_open_training(self):
        return self._open_action("qms.training.assignment", [("company_id", "=", self.company_id.id), ("state", "in", ["expired", "failed", "assigned"])], "Training Gaps")

    def action_open_audits(self):
        return self._open_action("qms.audit", [("company_id", "=", self.company_id.id), ("state", "!=", "closed")], "Open Audits")

    def action_open_complaints(self):
        return self._open_action("qms.complaint", [("company_id", "=", self.company_id.id), ("state", "not in", ["closed", "cancelled"])], "Open Customer Complaints")

    def action_open_calibration(self):
        return self._open_action("qms.measurement.equipment", [("company_id", "=", self.company_id.id), ("state", "=", "overdue")], "Overdue Calibration")

    def action_open_improvements(self):
        return self._open_action("qms.improvement", [("company_id", "=", self.company_id.id), ("status", "not in", ["completed", "standardized", "cancelled"])], "Open Improvements")


    @api.model
    def _cron_weekly_digest(self):
        companies = self.env["res.company"].search([])
        manager_group = self.env.ref("qms_core.group_qms_manager", raise_if_not_found=False)
        if not manager_group:
            return True
        for company in companies:
            snapshot = self.search([("company_id", "=", company.id)], limit=1) or self.create({"company_id": company.id})
            snapshot.action_refresh()
            recipients = manager_group.users.filtered(lambda u: u.company_ids and u.email and company in u.company_ids)
            if not recipients:
                continue
            body = (
                "<p><strong>QMS Weekly Management Digest</strong></p>"
                "<ul>"
                "<li>Readiness Index: %.2f%%</li>"
                "<li>Open NCR: %s</li>"
                "<li>Overdue CAPA: %s</li>"
                "<li>High/Critical Risks: %s</li>"
                "<li>Training Gaps: %s</li>"
                "<li>Compliance Gaps: %s</li>"
                "<li>Overdue Calibration: %s</li>"
                "</ul>"
            ) % (snapshot.readiness_index, snapshot.open_ncr_count, snapshot.overdue_capa_count, snapshot.high_risk_count, snapshot.training_gap_count, snapshot.compliance_gap_count, snapshot.overdue_calibration_count)
            self.env["mail.compose.message"].sudo().create({
                "subject": _("QMS Weekly Management Digest - %s") % company.name,
                "body": body,
                "composition_mode": "comment",
                "partner_ids": [(6, 0, recipients.mapped("partner_id").ids)],
                "model": "qms.dashboard",
                "res_id": snapshot.id,
            }).send_mail()
        return True
