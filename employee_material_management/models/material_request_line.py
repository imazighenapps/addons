# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MaterialRequest(models.Model):
    _name = 'material.request.line'
    _description = 'Material Request Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']





    request_id      = fields.Many2one('material.request',string='Requisitions',)
    product_id      = fields.Many2one('product.product',string='Product', required=True,)
    description     = fields.Char(string='Description',required=True,)
    qty             = fields.Float(string='Quantity', default=1, required=True,)
    uom             = fields.Many2one('uom.uom',string='Unit of Measure',required=True,)
    state           = fields.Selection([('new','New'),('done','done')],default="new",string="State")
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id

    