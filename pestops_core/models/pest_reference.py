from odoo import fields, models


class PestCategory(models.Model):
    _name = 'pest.category'
    _description = 'Pest Category'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    _sql_constraints = [
        (
            'pest_category_name_company_uniq',
            'unique(name, company_id)',
            'The pest category name must be unique per company.',
        ),
    ]


class PestType(models.Model):
    _name = 'pest.type'
    _description = 'Pest Type'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    category_id = fields.Many2one(
        'pest.category',
        required=True,
        ondelete='restrict',
    )
    code = fields.Char()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text()
    risk_level = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    _sql_constraints = [
        (
            'pest_type_name_company_uniq',
            'unique(name, company_id)',
            'The pest type name must be unique per company.',
        ),
    ]


class TreatmentMethod(models.Model):
    _name = 'pest.treatment.method'
    _description = 'Treatment Method'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text()
    instructions = fields.Html()
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    _sql_constraints = [
        (
            'treatment_method_name_company_uniq',
            'unique(name, company_id)',
            'The treatment method name must be unique per company.',
        ),
    ]


class PestRiskLevel(models.Model):
    _name = 'pest.risk.level'
    _description = 'Pest Risk Level'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    code = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        required=True,
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    color = fields.Integer(default=0)
    description = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    _sql_constraints = [
        (
            'risk_level_code_company_uniq',
            'unique(code, company_id)',
            'A risk level code must be unique per company.',
        ),
    ]
