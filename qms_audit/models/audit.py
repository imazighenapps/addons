from odoo import _, api, fields, models
from odoo.exceptions import UserError




class QmsAuditTemplate(models.Model):
    _name = "qms.audit.template"
    _description = "QMS Audit Checklist Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    standard_id = fields.Many2one("qms.standard", check_company=True)
    active = fields.Boolean(default=True)
    line_ids = fields.One2many("qms.audit.template.line", "template_id")

    def action_create_audit(self):
        self.ensure_one()
        audit = self.env["qms.audit"].create({"name": self.name, "company_id": self.company_id.id, "audit_type": "internal", "scope": self.name, "criteria": self.standard_id.name if self.standard_id else "Management system criteria", "requirement_ids": [(6, 0, self.line_ids.mapped("requirement_id").ids)]})
        self.env["qms.audit.line"].create([{
            "audit_id": audit.id, "sequence": line.sequence, "requirement_id": line.requirement_id.id,
            "question": line.question, "criterion": line.criterion, "method": line.method,
        } for line in self.line_ids])
        return {"type": "ir.actions.act_window", "res_model": "qms.audit", "res_id": audit.id, "view_mode": "form"}


class QmsAuditTemplateLine(models.Model):
    _name = "qms.audit.template.line"
    _description = "QMS Audit Template Line"
    _order = "sequence, id"

    template_id = fields.Many2one("qms.audit.template", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    requirement_id = fields.Many2one("qms.requirement", ondelete="restrict", check_company=True)
    question = fields.Char(required=True)
    criterion = fields.Text()
    method = fields.Selection([("document", "Document Review"), ("interview", "Interview"), ("observation", "Observation"), ("sampling", "Sampling"), ("system", "System Record")], default="document", required=True)

class QmsAuditProgram(models.Model):
    _name = "qms.audit.program"
    _description = "QMS Audit Program"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "year desc, name"

    name = fields.Char(required=True, tracking=True)
    year = fields.Integer(default=lambda self: fields.Date.today().year, required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    objective = fields.Text()
    cycle_type = fields.Selection([("annual", "Annual"), ("quarterly", "Quarterly"), ("monthly", "Monthly"), ("ad_hoc", "Ad Hoc")], default="annual", required=True)
    risk_review_date = fields.Date(string="Risk Review Date")
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user, check_company=True)
    risk_based = fields.Boolean(default=True, tracking=True)
    audit_ids = fields.One2many("qms.audit", "program_id")
    audit_count = fields.Integer(compute="_compute_audit_count")
    closed_audit_count = fields.Integer(compute="_compute_audit_count")
    completion_rate = fields.Float(compute="_compute_audit_count", digits=(16, 2))

    @api.depends("audit_ids", "audit_ids.state")
    def _compute_audit_count(self):
        for record in self:
            total = len(record.audit_ids)
            closed = len(record.audit_ids.filtered(lambda a: a.state == "closed"))
            record.audit_count = total
            record.closed_audit_count = closed
            record.completion_rate = closed / total * 100.0 if total else 0.0


class QmsAudit(models.Model):
    _name = "qms.audit"
    _description = "QMS Audit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "planned_date desc, code desc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.audit"), index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    program_id = fields.Many2one("qms.audit.program", ondelete="restrict", check_company=True)
    audit_type = fields.Selection([("internal", "Internal"), ("supplier", "Supplier"), ("customer", "Customer"), ("certification", "Certification"), ("surveillance", "Surveillance"), ("regulatory", "Regulatory"), ("process", "Process"), ("product", "Product")], default="internal", required=True)
    scope = fields.Text(required=True)
    objective = fields.Text()
    criteria = fields.Text()
    lead_auditor_id = fields.Many2one("res.users", string="Lead Auditor", required=True, default=lambda self: self.env.user, check_company=True)
    auditee_owner_id = fields.Many2one("res.users", string="Auditee Process Owner", check_company=True)
    opening_meeting_done = fields.Boolean(default=False)
    closing_meeting_done = fields.Boolean(default=False)
    auditor_ids = fields.Many2many("res.users", "qms_audit_auditor_rel", "audit_id", "user_id", string="Audit Team")
    process_ids = fields.Many2many("qms.process", "qms_audit_process_rel", "audit_id", "process_id", string="Processes")
    requirement_ids = fields.Many2many("qms.requirement", "qms_audit_requirement_rel", "audit_id", "requirement_id", string="Requirements")
    planned_date = fields.Date()
    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection([("planned", "Planned"), ("scheduled", "Scheduled"), ("in_progress", "In Progress"), ("report", "Report"), ("closed", "Closed")], default="planned", tracking=True, required=True, index=True)
    line_ids = fields.One2many("qms.audit.line", "audit_id", string="Audit Checks")
    finding_ids = fields.One2many("qms.finding", "audit_id", string="Findings")
    required_competency_ids = fields.Many2many("qms.competency.requirement", "qms_audit_competency_rel", "audit_id", "competency_id", string="Required Auditor Competencies")
    auditor_competence_status = fields.Selection([("not_checked", "Not Checked"), ("ok", "Competence Confirmed"), ("gap", "Competence Gap")], compute="_compute_auditor_competence")
    risk_based = fields.Boolean(default=True, tracking=True)
    risk_review_date = fields.Date(string="Risk Review Date")
    cycle_type = fields.Selection([("annual", "Annual"), ("quarterly", "Quarterly"), ("monthly", "Monthly"), ("ad_hoc", "Ad Hoc")], default="annual")
    risk_basis = fields.Text()
    sampling_plan = fields.Text()
    line_count = fields.Integer(compute="_compute_stats")
    conform_count = fields.Integer(compute="_compute_stats")
    compliance_rate = fields.Float(compute="_compute_stats", digits=(16, 2))

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Audit codes must be unique per company.",
    )

    @api.depends("lead_auditor_id", "required_competency_ids")
    def _compute_auditor_competence(self):
        competency_model = self.env["qms.employee.competency"]
        for record in self:
            if not record.required_competency_ids:
                record.auditor_competence_status = "not_checked"
                continue
            qualified = competency_model.search_count([("employee_id", "=", record.lead_auditor_id.id), ("requirement_id", "in", record.required_competency_ids.ids), ("status", "=", "qualified")])
            record.auditor_competence_status = "ok" if qualified == len(record.required_competency_ids) else "gap"

    @api.depends("line_ids", "line_ids.result")
    def _compute_stats(self):
        for record in self:
            checked = record.line_ids.filtered(lambda line: line.result and line.result != "na")
            conform = checked.filtered(lambda line: line.result == "conform")
            record.line_count = len(record.line_ids)
            record.conform_count = len(conform)
            record.compliance_rate = (len(conform) / len(checked) * 100.0) if checked else 0.0

    @api.constrains("lead_auditor_id", "auditee_owner_id")
    def _check_independence(self):
        for record in self:
            if record.lead_auditor_id and record.auditee_owner_id and record.lead_auditor_id == record.auditee_owner_id:
                raise UserError(_("The lead auditor cannot be the auditee process owner."))

    def action_schedule(self):
        self.write({"state": "scheduled"})
        return True

    def action_start(self):
        for record in self:
            if record.risk_based and not record.risk_basis:
                raise UserError(_("Document the risk basis before starting a risk-based audit."))
            if record.auditor_competence_status == "gap":
                raise UserError(_("Resolve the lead-auditor competence gap before starting the audit."))
            if not record.line_ids:
                raise UserError(_("Add at least one audit check before starting the audit."))
        self.write({"state": "in_progress", "start_date": fields.Date.context_today(self)})
        return True

    def action_generate_report(self):
        for record in self:
            if any(not line.result for line in record.line_ids):
                raise UserError(_("Every audit check must have a result before generating the report."))
        self.write({"state": "report"})
        return True

    def action_close(self):
        for record in self:
            if record.state != "report":
                raise UserError(_("An audit must be in Report state before it can be closed."))
            if any(not line.result for line in record.line_ids):
                raise UserError(_("Every audit check must have a result before closing the audit."))
        self.write({"state": "closed", "end_date": fields.Date.context_today(self)})
        return True


class QmsAuditLine(models.Model):
    _name = "qms.audit.line"
    _description = "QMS Audit Check"
    _order = "sequence, id"

    audit_id = fields.Many2one("qms.audit", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one("res.company", related="audit_id.company_id", store=True, index=True, readonly=True)
    sequence = fields.Integer(default=10)
    requirement_id = fields.Many2one("qms.requirement", ondelete="restrict", check_company=True)
    question = fields.Char(required=True)
    criterion = fields.Text()
    method = fields.Selection([("document", "Document Review"), ("interview", "Interview"), ("observation", "Observation"), ("sampling", "Sampling"), ("system", "System Record")], default="document", required=True)
    result = fields.Selection([("conform", "Conform"), ("observation", "Observation"), ("minor", "Minor NC"), ("major", "Major NC"), ("na", "Not Applicable")])
    note = fields.Text()
    evidence_ids = fields.Many2many("qms.evidence", "qms_audit_line_evidence_rel", "line_id", "evidence_id", string="Evidence")


class QmsFinding(models.Model):
    _name = "qms.finding"
    _description = "QMS Audit Finding"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "severity desc, id desc"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    audit_id = fields.Many2one("qms.audit", required=True, ondelete="cascade", check_company=True)
    audit_line_id = fields.Many2one("qms.audit.line", ondelete="set null")
    severity = fields.Selection([("observation", "Observation"), ("minor", "Minor"), ("major", "Major")], default="minor", required=True, tracking=True)
    description = fields.Text(required=True)
    requirement_id = fields.Many2one("qms.requirement", ondelete="restrict", check_company=True)
    evidence_ids = fields.Many2many("qms.evidence", "qms_finding_evidence_rel", "finding_id", "evidence_id")
    state = fields.Selection([("open", "Open"), ("converted", "Converted to NCR"), ("closed", "Closed")], default="open", tracking=True)
