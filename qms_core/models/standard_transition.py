from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class QmsStandardMapping(models.Model):
    _name = "qms.standard.mapping"
    _description = "Requirement Mapping Between Standard Editions"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "source_standard_id, source_requirement_id, target_requirement_id"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    source_standard_id = fields.Many2one("qms.standard", required=True, ondelete="restrict", check_company=True)
    target_standard_id = fields.Many2one("qms.standard", required=True, ondelete="restrict", check_company=True)
    source_requirement_id = fields.Many2one("qms.requirement", string="Source Requirement", required=True, ondelete="restrict", check_company=True)
    target_requirement_id = fields.Many2one("qms.requirement", string="Target Requirement", ondelete="restrict", check_company=True)
    mapping_type = fields.Selection([
        ("equivalent", "Equivalent"), ("changed", "Changed"), ("new", "New"),
        ("removed", "Removed"), ("merged", "Merged"), ("split", "Split"),
    ], required=True, default="equivalent", tracking=True)
    impact = fields.Selection([("none", "No Impact"), ("low", "Low"), ("medium", "Medium"), ("high", "High")], default="medium", required=True)
    transition_action = fields.Text()
    status = fields.Selection([("open", "Open"), ("assessed", "Assessed"), ("migrated", "Migrated"), ("not_applicable", "Not Applicable")], default="open", required=True, tracking=True)
    notes = fields.Text()
    transition_id = fields.Many2one("qms.standard.transition", string="Transition Plan", ondelete="set null", check_company=True)

    @api.constrains("source_standard_id", "target_standard_id", "source_requirement_id", "target_requirement_id", "company_id")
    def _check_mapping(self):
        for record in self:
            if record.source_standard_id.company_id != record.company_id or record.target_standard_id.company_id != record.company_id:
                raise ValidationError(_("Both standards must belong to the selected company."))
            if record.source_requirement_id.standard_id != record.source_standard_id:
                raise ValidationError(_("The source requirement must belong to the source standard."))
            if record.target_requirement_id and record.target_requirement_id.standard_id != record.target_standard_id:
                raise ValidationError(_("The target requirement must belong to the target standard."))
            if record.source_requirement_id == record.target_requirement_id:
                raise ValidationError(_("Source and target requirements cannot be identical."))


class QmsStandardTransition(models.Model):
    _name = "qms.standard.transition"
    _description = "Standard Edition Transition Plan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "deadline, id"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, default=lambda self: self.env["ir.sequence"].next_by_code("qms.standard.transition"), required=True, index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    source_standard_id = fields.Many2one("qms.standard", string="From Standard", required=True, ondelete="restrict", check_company=True)
    target_standard_id = fields.Many2one("qms.standard", string="To Standard", required=True, ondelete="restrict", check_company=True)
    owner_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user, check_company=True)
    deadline = fields.Date()
    state = fields.Selection([("planned", "Planned"), ("assessing", "Assessing"), ("in_progress", "In Progress"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="planned", required=True, tracking=True)
    mapping_ids = fields.One2many("qms.standard.mapping", "transition_id", string="Requirement Mappings")
    mapping_count = fields.Integer(compute="_compute_completion")
    migrated_count = fields.Integer(compute="_compute_completion")
    completion_percent = fields.Float(compute="_compute_completion", digits=(16, 2))
    scope = fields.Text()
    impact_summary = fields.Text()

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Transition codes must be unique per company.",
    )

    @api.depends("mapping_ids", "mapping_ids.status")
    def _compute_completion(self):
        for record in self:
            total = len(record.mapping_ids)
            migrated = len(record.mapping_ids.filtered(lambda m: m.status in ("migrated", "not_applicable")))
            record.mapping_count = total
            record.migrated_count = migrated
            record.completion_percent = migrated / total * 100.0 if total else 0.0

    @api.constrains("source_standard_id", "target_standard_id", "company_id")
    def _check_standards(self):
        for record in self:
            if record.source_standard_id == record.target_standard_id:
                raise ValidationError(_("The source and target standards must be different."))
            if record.source_standard_id.company_id != record.company_id or record.target_standard_id.company_id != record.company_id:
                raise ValidationError(_("Both standards must belong to the selected company."))

    def action_start_assessment(self):
        self.write({"state": "assessing"})
        return True

    def action_start(self):
        self.write({"state": "in_progress"})
        return True

    def action_complete(self):
        for record in self:
            if record.mapping_ids and any(m.status not in ("migrated", "not_applicable") for m in record.mapping_ids):
                raise UserError(_("Complete every standard mapping before closing the transition."))
        self.write({"state": "completed"})
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True
