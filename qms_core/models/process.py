from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QmsProcess(models.Model):
    _name = "qms.process"
    _description = "Management Process"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, code, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, index=True, tracking=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    owner_id = fields.Many2one("res.users", string="Process Owner", check_company=True)
    input_description = fields.Text(string="Inputs")
    output_description = fields.Text(string="Outputs")
    objective = fields.Text()
    active = fields.Boolean(default=True, tracking=True)
    requirement_ids = fields.Many2many("qms.requirement", "qms_requirement_process_rel", "process_id", "requirement_id", string="Requirements")
    risk_ids = fields.Many2many("qms.risk", "qms_process_risk_rel", "process_id", "risk_id", string="Risks")
    control_ids = fields.One2many("qms.control", "process_id", string="Controls")
    requirement_count = fields.Integer(compute="_compute_counts")
    risk_count = fields.Integer(compute="_compute_counts")
    control_count = fields.Integer(compute="_compute_counts")

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Process codes must be unique per company.",
    )

    @api.depends("requirement_ids", "risk_ids", "control_ids")
    def _compute_counts(self):
        for record in self:
            record.requirement_count = len(record.requirement_ids)
            record.risk_count = len(record.risk_ids)
            record.control_count = len(record.control_ids)

    @api.constrains("owner_id", "company_id")
    def _check_owner_company(self):
        for record in self:
            if record.owner_id and record.owner_id.company_id and record.owner_id.company_id != record.company_id:
                raise ValidationError(_("The process owner must belong to the same company."))
