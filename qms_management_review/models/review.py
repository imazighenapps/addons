from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class QmsManagementReview(models.Model):
    _name = "qms.management.review"
    _description = "QMS Management Review"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "meeting_date desc, code desc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.management.review"), index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    meeting_date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    period_start = fields.Date()
    period_end = fields.Date()
    chair_id = fields.Many2one("res.users", string="Chair", default=lambda self: self.env.user, check_company=True)
    attendee_ids = fields.Many2many("res.users", "qms_review_attendee_rel", "review_id", "user_id", string="Attendees")
    state = fields.Selection([("draft", "Draft"), ("prepared", "Prepared"), ("held", "Held"), ("closed", "Closed")], default="draft", required=True, tracking=True)

    closed_audit_count = fields.Integer(readonly=True)
    open_ncr_count = fields.Integer(readonly=True)
    overdue_capa_count = fields.Integer(readonly=True)
    high_risk_count = fields.Integer(readonly=True)
    objective_at_risk_count = fields.Integer(readonly=True)
    expired_training_count = fields.Integer(readonly=True)
    open_complaint_count = fields.Integer(readonly=True)
    overdue_calibration_count = fields.Integer(readonly=True)
    open_opportunity_count = fields.Integer(readonly=True)
    compliance_gap_count = fields.Integer(readonly=True)
    context_summary = fields.Text()
    supplier_summary = fields.Text()
    measurement_summary = fields.Text()
    improvement_summary = fields.Text()

    audit_summary = fields.Text()
    ncr_capa_summary = fields.Text()
    risk_summary = fields.Text()
    objective_summary = fields.Text()
    people_summary = fields.Text()
    resource_needs = fields.Text()
    decisions = fields.Text()
    action_ids = fields.One2many("qms.management.action", "review_id", string="Actions")
    action_count = fields.Integer(compute="_compute_action_count")

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Management review codes must be unique per company.",
    )

    @api.depends("action_ids")
    def _compute_action_count(self):
        for record in self:
            record.action_count = len(record.action_ids)

    def action_prepare_snapshot(self):
        for record in self:
            end = record.period_end or record.meeting_date or fields.Date.context_today(record)
            start = record.period_start or (end - timedelta(days=365))

            audits = self.env["qms.audit"].search([("company_id", "=", record.company_id.id), ("state", "=", "closed"), ("end_date", ">=", start), ("end_date", "<=", end)])
            ncrs = self.env["qms.ncr"].search([("company_id", "=", record.company_id.id), ("status", "!=", "closed")])
            capas = self.env["qms.capa"].search([("company_id", "=", record.company_id.id), ("deadline", "<", end), ("status", "not in", ["effective", "cancelled"] )])
            risks = self.env["qms.risk"].search([("company_id", "=", record.company_id.id), ("residual_level", "in", ["high", "critical"])])
            objectives = self.env["qms.objective"].search([("company_id", "=", record.company_id.id), ("status", "in", ["at_risk", "delayed"])])
            trainings = self.env["qms.training.assignment"].search([("company_id", "=", record.company_id.id), ("state", "=", "expired")])
            complaints = self.env["qms.complaint"].search([("company_id", "=", record.company_id.id), ("state", "not in", ["closed", "cancelled"])])
            calibrations = self.env["qms.measurement.equipment"].search([("company_id", "=", record.company_id.id), ("state", "=", "overdue")])
            opportunities = self.env["qms.opportunity"].search([("company_id", "=", record.company_id.id), ("status", "in", ["identified", "approved", "in_progress"])])
            gaps = self.env["qms.requirement"].search([("company_id", "=", record.company_id.id), ("compliance_state", "=", "missing")])
            contexts = self.env["qms.context.issue"].search([("company_id", "=", record.company_id.id), ("active", "=", True)])
            suppliers = self.env["qms.supplier"].search([("company_id", "=", record.company_id.id)])

            record.write({
                "closed_audit_count": len(audits),
                "open_ncr_count": len(ncrs),
                "overdue_capa_count": len(capas),
                "high_risk_count": len(risks),
                "objective_at_risk_count": len(objectives),
                "expired_training_count": len(trainings),
                "open_complaint_count": len(complaints),
                "overdue_calibration_count": len(calibrations),
                "open_opportunity_count": len(opportunities),
                "compliance_gap_count": len(gaps),
                "context_summary": f"{len(contexts)} open context issues require review.",
                "supplier_summary": f"{len(suppliers)} suppliers are currently registered in the QMS scope.",
                "measurement_summary": f"{len(calibrations)} measurement equipment records are overdue for calibration.",
                "improvement_summary": f"{len(opportunities)} improvement opportunities are open or in progress.",
                "audit_summary": f"{len(audits)} closed audits during the selected period.",
                "ncr_capa_summary": f"{len(ncrs)} open NCRs and {len(capas)} overdue CAPA actions at snapshot date.",
                "risk_summary": f"{len(risks)} risks currently rated High or Critical on residual exposure.",
                "objective_summary": f"{len(objectives)} objectives are At Risk or Delayed.",
                "people_summary": f"{len(trainings)} completed training assignments are expired.",
                "state": "prepared",
            })
        return True

    def action_mark_held(self):
        for record in self:
            if record.state != "prepared":
                raise UserError(_("Prepare the management review snapshot before marking the meeting as held."))
        self.write({"state": "held"})
        return True

    def action_close(self):
        for record in self:
            if record.state != "held":
                raise UserError(_("A management review must be held before it can be closed."))
            if any(action.status not in ("done", "cancelled") for action in record.action_ids):
                raise UserError(_("Complete or cancel every management-review action before closing the review."))
        self.write({"state": "closed"})
        return True


class QmsManagementAction(models.Model):
    _name = "qms.management.action"
    _description = "QMS Management Review Action"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "due_date, id"

    review_id = fields.Many2one("qms.management.review", required=True, ondelete="cascade", check_company=True)
    company_id = fields.Many2one("res.company", related="review_id.company_id", store=True, index=True, readonly=True)
    name = fields.Char(required=True, tracking=True)
    owner_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user, check_company=True)
    due_date = fields.Date()
    description = fields.Text()
    status = fields.Selection([("planned", "Planned"), ("in_progress", "In Progress"), ("done", "Done"), ("cancelled", "Cancelled")], default="planned", required=True, tracking=True)

    def action_start(self):
        self.write({"status": "in_progress"})
        return True

    def action_done(self):
        self.write({"status": "done"})
        return True

    def action_cancel(self):
        self.write({"status": "cancelled"})
        return True
