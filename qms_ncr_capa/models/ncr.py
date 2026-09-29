from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class QmsNcr(models.Model):
    _name = "qms.ncr"
    _description = "QMS Non-Conformity"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.ncr"), index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    source = fields.Selection([("audit", "Audit"), ("complaint", "Customer Complaint"), ("supplier", "Supplier"), ("process", "Process"), ("inspection", "Inspection"), ("other", "Other")], default="audit", required=True)
    severity = fields.Selection([("minor", "Minor"), ("major", "Major"), ("critical", "Critical")], default="minor", required=True, tracking=True)
    audit_id = fields.Many2one("qms.audit", ondelete="set null", check_company=True)
    finding_id = fields.Many2one("qms.finding", ondelete="set null", check_company=True)
    requirement_id = fields.Many2one("qms.requirement", ondelete="restrict", check_company=True)
    process_id = fields.Many2one("qms.process", ondelete="restrict", check_company=True)
    description = fields.Text(required=True)
    containment = fields.Text()
    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.user, check_company=True)
    root_cause_method = fields.Selection([("five_whys", "5 Whys"), ("ishikawa", "Ishikawa / Fishbone"), ("eight_d", "8D"), ("a3", "A3"), ("custom", "Custom")], default="five_whys", required=True)
    root_cause = fields.Text()
    root_cause_analysis = fields.Text()
    status = fields.Selection([("new", "New"), ("containment", "Containment"), ("analysis", "Root Cause Analysis"), ("action", "Action Plan"), ("effectiveness", "Effectiveness"), ("closed", "Closed")], default="new", required=True, tracking=True, index=True)
    capa_ids = fields.One2many("qms.capa", "ncr_id", string="CAPA")
    all_capa_effective = fields.Boolean(compute="_compute_capa_state")

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "NCR codes must be unique per company.",
    )

    @api.depends("capa_ids", "capa_ids.status")
    def _compute_capa_state(self):
        for record in self:
            record.all_capa_effective = bool(record.capa_ids) and all(capa.status == "effective" for capa in record.capa_ids)

    @api.constrains("audit_id", "finding_id")
    def _check_finding_audit(self):
        for record in self:
            if record.finding_id and record.audit_id and record.finding_id.audit_id != record.audit_id:
                raise ValidationError(_("The finding must belong to the selected audit."))

    def action_start_containment(self):
        for record in self:
            if record.status != "new":
                raise UserError(_("Containment can only be started from a new NCR."))
        self.write({"status": "containment"})
        return True

    def action_start_analysis(self):
        for record in self:
            if record.status != "containment":
                raise UserError(_("Root-cause analysis can only start after containment."))
            if not record.containment:
                raise UserError(_("Record the containment or immediate correction before root-cause analysis."))
        self.write({"status": "analysis"})
        return True

    def action_open_action_plan(self):
        for record in self:
            if record.status != "analysis":
                raise UserError(_("The action plan can only be opened after root-cause analysis."))
            if not record.root_cause:
                raise UserError(_("Document the root cause before opening the action plan."))
        self.write({"status": "action"})
        return True

    def action_verify_effectiveness(self):
        for record in self:
            if record.status != "action":
                raise UserError(_("Effectiveness verification can only start from the action-plan stage."))
            if not record.capa_ids:
                raise UserError(_("Create at least one CAPA before effectiveness verification."))
            if any(capa.status not in ("implemented", "effective") for capa in record.capa_ids):
                raise UserError(_("All CAPA actions must be implemented before effectiveness verification."))
        self.write({"status": "effectiveness"})
        return True

    def action_close(self):
        for record in self:
            if not record.all_capa_effective:
                raise UserError(_("Every CAPA must be verified effective before closing the NCR."))
        self.write({"status": "closed"})
        findings = self.mapped("finding_id")
        if findings:
            findings.write({"state": "converted"})
        return True


class QmsCapa(models.Model):
    _name = "qms.capa"
    _description = "QMS Corrective and Preventive Action"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "deadline, id"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.capa"), index=True)
    company_id = fields.Many2one("res.company", related="ncr_id.company_id", store=True, index=True, readonly=True)
    ncr_id = fields.Many2one("qms.ncr", required=True, ondelete="cascade", check_company=True)
    action_type = fields.Selection([("corrective", "Corrective"), ("preventive", "Preventive"), ("correction", "Correction")], default="corrective", required=True)
    action_description = fields.Text(required=True)
    owner_id = fields.Many2one("res.users", string="Owner", required=True, default=lambda self: self.env.user, check_company=True)
    deadline = fields.Date()
    implementation_date = fields.Date()
    verification_date = fields.Date()
    verification_method = fields.Text()
    effectiveness_note = fields.Text()
    status = fields.Selection([("planned", "Planned"), ("in_progress", "In Progress"), ("implemented", "Implemented"), ("effective", "Effective"), ("ineffective", "Ineffective"), ("cancelled", "Cancelled")], default="planned", tracking=True, required=True)
    evidence_ids = fields.Many2many("qms.evidence", "qms_capa_evidence_rel", "capa_id", "evidence_id", string="Evidence")

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "CAPA codes must be unique per company.",
    )

    def action_start(self):
        self.write({"status": "in_progress"})
        return True

    def action_mark_implemented(self):
        for record in self:
            if not record.implementation_date:
                raise UserError(_("Set the implementation date before marking the CAPA implemented."))
        self.write({"status": "implemented"})
        return True

    def action_mark_effective(self):
        for record in self:
            if not record.verification_date or not record.verification_method:
                raise UserError(_("Record the verification date and method before marking effectiveness."))
        self.write({"status": "effective"})
        return True

    def action_mark_ineffective(self):
        for record in self:
            record.status = "ineffective"
            if record.ncr_id:
                record.ncr_id.status = "action"
        return True


class QmsFindingNcrBridge(models.Model):
    _inherit = "qms.finding"

    ncr_id = fields.Many2one("qms.ncr", string="NCR", readonly=True, copy=False)

    def action_create_ncr(self):
        self.ensure_one()
        if self.ncr_id:
            return {"type": "ir.actions.act_window", "res_model": "qms.ncr", "res_id": self.ncr_id.id, "view_mode": "form"}
        ncr = self.env["qms.ncr"].create({
            "name": self.name,
            "company_id": self.company_id.id,
            "source": "audit",
            "severity": {"observation": "minor", "minor": "major", "major": "critical"}.get(self.severity, "minor"),
            "audit_id": self.audit_id.id,
            "finding_id": self.id,
            "requirement_id": self.requirement_id.id,
            "description": self.description,
        })
        self.write({"ncr_id": ncr.id, "state": "converted"})
        return {"type": "ir.actions.act_window", "res_model": "qms.ncr", "res_id": ncr.id, "view_mode": "form"}
