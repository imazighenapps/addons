from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QmsControl(models.Model):
    _name = "qms.control"
    _description = "QMS Control"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(default=lambda self: self.env["ir.sequence"].next_by_code("qms.control"), required=True, copy=False, index=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    process_id = fields.Many2one("qms.process", ondelete="restrict", check_company=True)
    control_type = fields.Selection([("preventive", "Preventive"), ("detective", "Detective"), ("corrective", "Corrective")], default="preventive", required=True)
    frequency = fields.Selection([("event", "Per Event"), ("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual")], default="event", required=True)
    owner_id = fields.Many2one("res.users", string="Control Owner", check_company=True)
    description = fields.Text()
    operation = fields.Text(string="Expected Operation")
    evidence_expected = fields.Boolean(default=True)
    active = fields.Boolean(default=True, tracking=True)
    requirement_ids = fields.Many2many("qms.requirement", "qms_requirement_control_rel", "control_id", "requirement_id", string="Requirements")
    risk_ids = fields.Many2many("qms.risk", "qms_risk_control_rel", "control_id", "risk_id", string="Risks")

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Control codes must be unique per company.",
    )

    @api.constrains("owner_id", "company_id")
    def _check_owner_company(self):
        for record in self:
            if record.owner_id and record.owner_id.company_id and record.owner_id.company_id != record.company_id:
                raise ValidationError(_("The control owner must belong to the same company."))
