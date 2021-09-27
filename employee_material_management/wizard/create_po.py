# -*- coding: utf-8 -*-


from odoo import models, fields,api

class CreatePo(models.TransientModel):
    _name = 'create.po'

    partner_id = fields.Many2one('res.partner',string="Partner", required="1")
    line_ids   = field_name = fields.One2many('create.po.line', 'cpo_id', string='PO Lines')



    def do_create_po(self):
        line_val = []
        po_id = self.env['purchase.order'].create({ 'partner_id'  : self.partner_id.id,
                                                    'currency_id' : self.env.user.company_id.currency_id.id,
                                                    'date_order' : fields.Date.today(),
                                                    'company_id' : self.env.user.company_id.id,     
                                                        })   
        for line in self.line_ids:
            if line.include :
                line_val.append({"product_id"  : line.product_id.id,
                                "name"         : line.description,
                                "product_qty"  : line.qty,
                                "product_uom"  : line.uom.id,
                                "order_id"     : po_id.id,
                                'date_planned' : fields.Date.today(),
                                'state'        : 'draft',
                                })
                line.request_line_id.state = 'done'                
            
        for lv in  line_val:
            self.env["purchase.order.line"].create(lv)    

        purchase_action = self.env.ref('purchase.purchase_rfq')
        purchase_action = purchase_action.read()[0]
        purchase_action['domain'] = str([('id','=',po_id.id)])    
        return  purchase_action


class CreatePoline(models.TransientModel):
    _name = 'create.po.line'

    cpo_id          = fields.Many2one('create.po',string='CPO',)
    product_id      = fields.Many2one('product.product',string='Product',)
    description     = fields.Char(string='Description',)
    qty             = fields.Float(string='Quantity', default=1,)
    uom             = fields.Many2one('uom.uom',string='Unit of Measure')
    include         = fields.Boolean(' ')
    request_line_id = fields.Many2one('material.request.line',string='Material request line',)
    