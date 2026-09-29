from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QmsRisk(models.Model):
    _name = "qms.risk"
    _description = "QMS Risk"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "inherent_score desc, code"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(default=lambda self: self.env["ir.sequence"].next_by_code("qms.risk"), required=True, copy=False, index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    process_id = fields.Many2one("qms.process", ondelete="restrict", index=True, check_company=True)
    category = fields.Selection(
        [("quality", "Quality"), ("operational", "Operational"), ("compliance", "Compliance"), ("safety", "Safety"), ("environment", "Environmental"), ("strategic", "Strategic"), ("other", "Other")],
        default="quality",
        required=True,
    )
    description = fields.Text(required=True)
    owner_id = fields.Many2one("res.users", string="Owner", check_company=True)
    likelihood = fields.Integer(default=1)
    impact = fields.Integer(default=1)
    inherent_score = fields.Integer(compute="_compute_scores", store=True)
    inherent_level = fields.Selection([("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")], compute="_compute_scores", store=True)
    residual_likelihood = fields.Integer(default=1)
    residual_impact = fields.Integer(default=1)
    residual_score = fields.Integer(compute="_compute_scores", store=True)
    residual_level = fields.Selection([("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")], compute="_compute_scores", store=True)
    treatment = fields.Text()
    treatment_due_date = fields.Date()
    state = fields.Selection([("identified", "Identified"), ("assessed", "Assessed"), ("treated", "Treatment Planned"), ("accepted", "Accepted")], default="identified", tracking=True)
    control_ids = fields.Many2many("qms.control", "qms_risk_control_rel", "risk_id", "control_id", string="Controls")
    requirement_ids = fields.Many2many("qms.requirement", "qms_requirement_risk_rel", "risk_id", "requirement_id", string="Requirements")

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Risk codes must be unique per company.",
    )

    @api.depends("likelihood", "impact", "residual_likelihood", "residual_impact")
    def _compute_scores(self):
        for record in self:
            record.inherent_score = record.likelihood * record.impact
            record.residual_score = record.residual_likelihood * record.residual_impact
            record.inherent_level = self._risk_level(record.inherent_score)
            record.residual_level = self._risk_level(record.residual_score)

    @staticmethod
    def _risk_level(score):
        if score >= 20:
            return "critical"
        if score >= 12:
            return "high"
        if score >= 5:
            return "medium"
        return "low"

    @api.constrains("likelihood", "impact", "residual_likelihood", "residual_impact")
    def _check_ratings(self):
        for record in self:
            values = [record.likelihood, record.impact, record.residual_likelihood, record.residual_impact]
            if any(value < 1 or value > 5 for value in values):
                raise ValidationError(_("Risk ratings must be integers from 1 to 5."))
