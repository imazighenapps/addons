from odoo import fields, models


class ContractClause(models.Model):
    _name = 'contract.clause'
    _description = 'Reusable Contract Clause'
    _order = 'category, sequence, name'

    name = fields.Char(string='Clause Title', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    category = fields.Selection([
        ('confidentiality', 'Confidentiality'),
        ('termination', 'Termination'),
        ('penalty', 'Penalties'),
        ('liability', 'Liability'),
        ('ip', 'Intellectual Property'),
        ('data_protection', 'Data Protection (GDPR)'),
        ('payment', 'Payment'),
        ('force_majeure', 'Force Majeure'),
        ('jurisdiction', 'Jurisdiction'),
        ('other', 'Other'),
    ], string='Category', required=True, default='other')
    content = fields.Html(string='Clause Content', required=True)
    description = fields.Char(string='Short Description')
    applicable_to = fields.Selection([
        ('all', 'All Contract Types'),
        ('customer', 'Customer Contracts Only'),
        ('supplier', 'Vendor Contracts Only'),
    ], string='Applicable To', default='all')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
    )
