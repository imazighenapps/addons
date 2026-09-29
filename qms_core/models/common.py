from odoo import fields, models


class QmsCompanyMixin(models.AbstractModel):
    _name = "qms.company.mixin"
    _description = "QMS Company Context"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
        check_company=True,
    )
