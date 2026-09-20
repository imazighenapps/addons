from odoo import fields, models


class SmartOperationsImpact(models.Model):
    _name = 'smart.operations.impact'
    _description = 'Operational Impact Snapshot'
    _order = 'id desc'

    issue_id = fields.Many2one('smart.operations.issue', required=True, ondelete='cascade')
    model_id = fields.Many2one('ir.model', ondelete='set null')
    res_id = fields.Integer()
    relation_type = fields.Selection([
        ('customer', 'Customer'), ('sales_order', 'Sales Order'), ('delivery', 'Delivery'),
        ('manufacturing', 'Manufacturing Order'), ('purchase', 'Purchase Order'), ('other', 'Other'),
    ], required=True)
    quantity = fields.Float()
    monetary_value = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='issue_id.currency_id', store=True)
    delay_days = fields.Float()
