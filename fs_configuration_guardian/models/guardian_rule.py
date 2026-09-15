from odoo import fields, models


class GuardianRule(models.Model):
    _name = 'fs.guardian.rule'
    _description = 'Configuration Guardian Rule'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    category = fields.Selection([
        ('security', 'Security'), ('automation', 'Automation'), ('studio', 'Studio'),
        ('accounting', 'Accounting'), ('inventory', 'Inventory'), ('sales', 'Sales'),
        ('technical', 'Technical'),
    ], required=True)
    model_name = fields.Char(required=True)
    risk_level = fields.Selection([
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')
    ], required=True, default='medium')
    description = fields.Text()
