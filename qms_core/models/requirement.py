from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class QmsRequirement(models.Model):
    _name = "qms.requirement"
    _description = "Management System Requirement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "standard_id, clause_id, sequence, code"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(default=lambda self: self.env["ir.sequence"].next_by_code("qms.requirement"), required=True, copy=False, index=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one("res.company", related="standard_id.company_id", store=True, index=True, readonly=True)
    standard_id = fields.Many2one("qms.standard", required=True, ondelete="restrict", index=True)
    clause_id = fields.Many2one("qms.standard.clause", required=True, ondelete="restrict", index=True)
    description = fields.Html()
    guidance = fields.Html()
    mandatory = fields.Boolean(default=True)
    active = fields.Boolean(default=True)
    implementation_status = fields.Selection([
        ("not_assessed", "Not Assessed"), ("planned", "Planned"),
        ("implemented", "Implemented"), ("partial", "Partially Implemented"),
        ("not_applicable", "Not Applicable"),
    ], default="not_assessed", required=True, tracking=True, index=True)
    assessment_date = fields.Date(readonly=True, tracking=True)
    assessed_by_id = fields.Many2one("res.users", readonly=True, check_company=True)

    process_ids = fields.Many2many("qms.process", "qms_requirement_process_rel", "requirement_id", "process_id", string="Processes")
    risk_ids = fields.Many2many("qms.risk", "qms_requirement_risk_rel", "requirement_id", "risk_id", string="Risks")
    control_ids = fields.Many2many("qms.control", "qms_requirement_control_rel", "requirement_id", "control_id", string="Controls")
    evidence_ids = fields.Many2many("qms.evidence", "qms_requirement_evidence_rel", "requirement_id", "evidence_id", string="Evidence")

    evidence_count = fields.Integer(compute="_compute_counts")
    control_count = fields.Integer(compute="_compute_counts")
    process_count = fields.Integer(compute="_compute_counts")
    risk_count = fields.Integer(compute="_compute_counts")

    compliance_state = fields.Selection(
        [
            ("missing", "Missing Evidence"),
            ("partial", "Partially Supported"),
            ("supported", "Supported"),
        ],
        compute="_compute_compliance_state",
        store=True,
        index=True,
    )

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Requirement codes must be unique per company.",
    )

    @api.depends("implementation_status", "evidence_ids", "evidence_ids.status")
    def _compute_compliance_state(self):
        for record in self:
            usable = record.evidence_ids.filtered(lambda evidence: evidence.status == "valid")
            if record.implementation_status == "not_applicable":
                record.compliance_state = "supported"
            elif not usable:
                record.compliance_state = "missing"
            elif record.implementation_status in ("partial", "planned", "not_assessed"):
                record.compliance_state = "partial"
            elif len(usable) == len(record.evidence_ids):
                record.compliance_state = "supported"
            else:
                record.compliance_state = "partial"

    @api.depends("evidence_ids", "control_ids", "process_ids", "risk_ids")
    def _compute_counts(self):
        for record in self:
            record.evidence_count = len(record.evidence_ids)
            record.control_count = len(record.control_ids)
            record.process_count = len(record.process_ids)
            record.risk_count = len(record.risk_ids)

    @api.constrains("clause_id", "standard_id")
    def _check_clause_standard(self):
        for record in self:
            if record.clause_id.standard_id != record.standard_id:
                raise ValidationError(_("The clause must belong to the selected standard."))

    def action_mark_supported(self):
        for record in self:
            if not record.evidence_ids.filtered(lambda evidence: evidence.status == "valid"):
                raise UserError(_("Add at least one valid evidence record before marking a requirement as supported."))
            record.write({"implementation_status": "implemented", "assessment_date": fields.Date.context_today(record), "assessed_by_id": self.env.user.id})
        return True

    def action_assess_partial(self):
        self.write({"implementation_status": "partial", "assessment_date": fields.Date.context_today(self), "assessed_by_id": self.env.user.id})
        return True

    def action_mark_not_applicable(self):
        self.write({"implementation_status": "not_applicable", "assessment_date": fields.Date.context_today(self), "assessed_by_id": self.env.user.id})
        return True
