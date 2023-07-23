from odoo import models, fields,api






class Service(models.Model):
    _name = 'appointment.service'
    _description = 'Service'
    _rec_name = "product_id"

    product_id      = fields.Many2one('product.product',string="Service" , domain=[('detailed_type','=','service')])
    duration        = fields.Float(string='Duration')
    company_id      = fields.Many2one('res.company', string='Company', required=True, readonly=True, index=True, default=lambda self: self.env.company)
    currency_id    = fields.Many2one(comodel_name='res.currency',string='Currency',related='company_id.currency_id')
    calendar_id      = fields.Many2one('appointment.calendar',string="calendar")

   
    cost            = fields.Monetary(string='Cost',currency_field="currency_id")
    resource_ids    = fields.Many2many('resource.resource', string='Resources')


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.cost = self.product_id.list_price
        else:
            self.cost = 0.0