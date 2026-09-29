from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class QmsQualityCost(models.Model):
    _name = "qms.quality.cost"
    _description = "QMS Cost of Quality"
    _order = "date desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    date = fields.Date(default=fields.Date.context_today, required=True)
    cost_type = fields.Selection([
        ("prevention", "Prevention"), ("appraisal", "Appraisal"),
        ("internal_failure", "Internal Failure"), ("external_failure", "External Failure")
    ], required=True)
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", readonly=True)
    ncr_id = fields.Many2one("qms.ncr", check_company=True)
    capa_id = fields.Many2one("qms.capa", check_company=True)
    description = fields.Text()

    @api.constrains("amount")
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError(_("Quality cost amounts cannot be negative."))
