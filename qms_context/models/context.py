from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class QmsContextIssue(models.Model):
    _name = "qms.context.issue"
    _description = "QMS Context Issue"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    issue_type = fields.Selection([
        ("internal", "Internal Issue"), ("external", "External Issue"),
    ], required=True, default="internal")
    category = fields.Selection([
        ("strategic", "Strategic"), ("customer", "Customer"), ("technology", "Technology"),
        ("people", "People"), ("regulatory", "Regulatory"), ("supply_chain", "Supply Chain"),
        ("environment", "Environment"), ("safety", "Health & Safety"), ("financial", "Financial"),
        ("other", "Other"),
    ], required=True, default="strategic")
    description = fields.Text(required=True)
    impact = fields.Text()
    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.user, check_company=True)
    review_date = fields.Date()
    active = fields.Boolean(default=True)
    status = fields.Selection([
        ("open", "Open"), ("in_progress", "In Progress"), ("resolved", "Resolved"), ("closed", "Closed")
    ], default="open", required=True, tracking=True)
    climate_relevance = fields.Selection([
        ("not_assessed", "Not Assessed"), ("not_relevant", "Not Relevant"),
        ("relevant", "Relevant"), ("material", "Material"),
    ], default="not_assessed", required=True)


class QmsInterestedParty(models.Model):
    _name = "qms.interested.party"
    _description = "QMS Interested Party"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "category, name"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    category = fields.Selection([
        ("customer", "Customer"), ("employee", "Employee / Worker"), ("supplier", "Supplier"),
        ("regulator", "Regulator"), ("owner", "Owner / Investor"), ("community", "Community"),
        ("partner", "Business Partner"), ("other", "Other"),
    ], required=True, default="customer")
    needs_expectations = fields.Text(required=True)
    requirements = fields.Text()
    monitoring_method = fields.Text()
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user, check_company=True)
    relevant = fields.Boolean(default=True)
    review_date = fields.Date()


class QmsManagementScope(models.Model):
    _name = "qms.management.scope"
    _description = "QMS Management Scope"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    scope_text = fields.Text(required=True)
    sites = fields.Text()
    products_services = fields.Text()
    processes = fields.Text()
    exclusions = fields.Text()
    effective_date = fields.Date()
    review_date = fields.Date()
    climate_relevance = fields.Selection([
        ("not_assessed", "Not Assessed"), ("not_relevant", "Not Relevant"),
        ("relevant", "Relevant"), ("material", "Material"),
    ], default="not_assessed", required=True)
    state = fields.Selection([
        ("draft", "Draft"), ("approved", "Approved"), ("superseded", "Superseded")
    ], default="draft", tracking=True)

    def action_approve(self):
        self.write({"state": "approved"})
        return True

    def action_supersede(self):
        self.write({"state": "superseded"})
        return True


class QmsComplianceObligation(models.Model):
    _name = "qms.compliance.obligation"
    _description = "QMS Compliance Obligation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "review_date, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.compliance.obligation"), index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    obligation_type = fields.Selection([
        ("legal", "Legal / Regulatory"), ("contractual", "Contractual"),
        ("customer", "Customer Requirement"), ("industry", "Industry / Voluntary"), ("internal", "Internal Commitment"),
    ], required=True, default="legal")
    source_reference = fields.Char()
    description = fields.Text(required=True)
    applicable_process_ids = fields.Many2many("qms.process", string="Applicable Processes")
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user, check_company=True)
    review_date = fields.Date(required=True)
    next_review_date = fields.Date()
    status = fields.Selection([
        ("identified", "Identified"), ("applicable", "Applicable"), ("not_applicable", "Not Applicable"),
        ("under_review", "Under Review"), ("compliant", "Compliant"), ("gap", "Gap Identified"),
    ], default="identified", required=True, tracking=True)
    evidence_ids = fields.Many2many("qms.evidence", string="Evidence")
    notes = fields.Text()

    @api.constrains("review_date", "next_review_date")
    def _check_dates(self):
        for record in self:
            if record.next_review_date and record.next_review_date < record.review_date:
                raise ValidationError(_("The next review date cannot be earlier than the current review date."))


class QmsOpportunity(models.Model):
    _name = "qms.opportunity"
    _description = "QMS Improvement Opportunity"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, target_date, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.opportunity"), index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    source = fields.Selection([
        ("audit", "Audit"), ("risk", "Risk Review"), ("complaint", "Customer Complaint"),
        ("objective", "Objective"), ("employee", "Employee Suggestion"), ("management_review", "Management Review"),
        ("other", "Other"),
    ], default="other", required=True)
    description = fields.Text(required=True)
    expected_benefit = fields.Text()
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user, check_company=True)
    priority = fields.Selection([("0", "Low"), ("1", "Normal"), ("2", "High"), ("3", "Strategic")], default="1", required=True)
    target_date = fields.Date()
    action_plan = fields.Text()
    status = fields.Selection([
        ("identified", "Identified"), ("approved", "Approved"), ("in_progress", "In Progress"),
        ("completed", "Completed"), ("rejected", "Rejected"),
    ], default="identified", required=True, tracking=True)
    result = fields.Text()

    def action_approve(self):
        self.write({"status": "approved"})
        return True

    def action_start(self):
        self.write({"status": "in_progress"})
        return True

    def action_complete(self):
        for record in self:
            if not record.result:
                raise UserError(_("Record the opportunity result before marking it completed."))
        self.write({"status": "completed"})
        return True

    def action_reject(self):
        self.write({"status": "rejected"})
        return True
