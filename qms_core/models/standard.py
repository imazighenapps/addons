from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QmsStandard(models.Model):
    _name = "qms.standard"
    _description = "Management System Standard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code, version"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, index=True, tracking=True)
    version = fields.Char(default="", tracking=True)
    edition = fields.Char(string="Edition", tracking=True, help="Edition label, e.g. 2026 or Rev. A.")
    publication_date = fields.Date(string="Publication Date")
    lifecycle_status = fields.Selection([
        ("draft", "Draft"), ("current", "Current"), ("superseded", "Superseded"), ("withdrawn", "Withdrawn")
    ], default="draft", required=True, tracking=True)
    standard_family = fields.Selection([
        ("quality", "Quality Management"), ("environment", "Environmental Management"),
        ("ohs", "Occupational Health & Safety"), ("food_safety", "Food Safety"),
        ("audit", "Auditing Guidelines"), ("measurement", "Measurement Management"),
        ("customer", "Customer Satisfaction"), ("other", "Other"),
    ], default="quality", required=True, index=True)
    is_certifiable = fields.Boolean(default=True)
    source_url = fields.Char(string="Official Reference URL")
    supersedes_id = fields.Many2one("qms.standard", string="Supersedes", ondelete="restrict", check_company=True)
    transition_due_date = fields.Date(string="Transition Due Date")
    transition_note = fields.Text(string="Transition Notes")
    mapping_count = fields.Integer(compute="_compute_mapping_count")
    transition_count = fields.Integer(compute="_compute_mapping_count")
    issuing_body = fields.Char(string="Issuing Body")
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    description = fields.Html()
    active = fields.Boolean(default=True, tracking=True)
    effective_date = fields.Date()
    review_date = fields.Date()
    clause_ids = fields.One2many("qms.standard.clause", "standard_id", string="Clauses")
    requirement_ids = fields.One2many("qms.requirement", "standard_id", string="Requirements")
    requirement_count = fields.Integer(compute="_compute_counts")
    clause_count = fields.Integer(compute="_compute_counts")

    _code_version_company_uniq = models.Constraint(
        "UNIQUE(code, version, company_id)",
        "A standard code/version must be unique per company.",
    )

    @api.depends("clause_ids", "requirement_ids")
    def _compute_counts(self):
        for record in self:
            record.clause_count = len(record.clause_ids)
            record.requirement_count = len(record.requirement_ids)

    @api.depends("requirement_ids", "supersedes_id")
    def _compute_mapping_count(self):
        mapping_model = self.env["qms.standard.mapping"]
        transition_model = self.env["qms.standard.transition"]
        for record in self:
            record.mapping_count = mapping_model.search_count([("company_id", "=", record.company_id.id), "|", ("source_standard_id", "=", record.id), ("target_standard_id", "=", record.id)])
            record.transition_count = transition_model.search_count([("company_id", "=", record.company_id.id), "|", ("source_standard_id", "=", record.id), ("target_standard_id", "=", record.id)])

    @api.constrains("effective_date", "review_date")
    def _check_dates(self):
        for record in self:
            if record.effective_date and record.review_date and record.review_date < record.effective_date:
                raise ValidationError(_("The review date cannot be earlier than the effective date."))

    def action_archive(self):
        self.write({"active": False})
        return True

    def action_activate(self):
        self.write({"active": True, "lifecycle_status": "current"})
        return True

    def action_set_current(self):
        for record in self:
            if not record.active:
                raise ValidationError(_("Activate the standard before making it current."))
            record.lifecycle_status = "current"
        return True

    def action_supersede(self):
        for record in self:
            record.write({"lifecycle_status": "superseded", "active": False})
        return True


class QmsStandardClause(models.Model):
    _name = "qms.standard.clause"
    _description = "Standard Clause"
    _order = "standard_id, sequence, code"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    standard_id = fields.Many2one("qms.standard", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one("res.company", related="standard_id.company_id", store=True, index=True, readonly=True)
    parent_id = fields.Many2one("qms.standard.clause", string="Parent Clause", ondelete="restrict")
    child_ids = fields.One2many("qms.standard.clause", "parent_id")
    requirement_ids = fields.One2many("qms.requirement", "clause_id")
    description = fields.Html()
    active = fields.Boolean(default=True)

    _clause_code_standard_uniq = models.Constraint(
        "UNIQUE(standard_id, code, company_id)",
        "Clause codes must be unique inside a standard.",
    )

    @api.constrains("parent_id")
    def _check_parent_standard(self):
        for record in self:
            if record.parent_id and record.parent_id.standard_id != record.standard_id:
                raise ValidationError(_("A clause parent must belong to the same standard."))
            if record.parent_id == record:
                raise ValidationError(_("A clause cannot be its own parent."))

    @api.onchange("standard_id")
    def _onchange_standard_id(self):
        if self.parent_id and self.standard_id and self.parent_id.standard_id != self.standard_id:
            self.parent_id = False
