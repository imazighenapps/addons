# -*- coding: utf-8 -*-


from odoo import models, fields,api

class CreatePicking(models.TransientModel):
    _name = 'create.picking'

    line_ids         = field_name = fields.One2many('create.picking.line', 'cpicking_id', string='PO Lines')
    picking_type_id  = fields.Many2one('stock.picking.type', 'Operation Type for Returns',check_company=True,required="1")
    location_dest_id = fields.Many2one('stock.location', 'Default Destination Location',check_company=True,required="1")
    location_src_id  = fields.Many2one('stock.location', 'Default Source Location',check_company=True,required="1")
    company_id       = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required=True,copy=True,)

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        if self.picking_type_id:
            self.location_dest_id = self.picking_type_id.default_location_dest_id.id
            self.location_src_id  = self.picking_type_id.default_location_src_id.id      


    def do_create_picking(self):
        line_val = []
        picking_id = self.env['stock.picking'].sudo().create({ 'scheduled_date' : fields.Date.today(),
                                                          'location_id' : self.location_src_id.id,
                                                          'location_dest_id' : self.location_dest_id.id,
                                                          'picking_type_id' : self.picking_type_id.id,
                                                          'origin' : self.env['material.request'].search([('id','=',self.env.context.get('active_id'))]).name,   
                                                        })   
        for line in self.line_ids:
            if line.include :
                line_val.append({'product_id' : line.product_id.id,
                                 'product_uom_qty' : line.qty,
                                 'qty_done' : line.qty,
                                 'product_uom_id' : line.uom.id,
                                 'location_id' : self.location_src_id.id,
                                 'location_dest_id' : self.location_dest_id.id,
                                 'picking_id' : picking_id.id,
                                })
                line.request_line_id.state = 'done'                
        for lv in  line_val:
            self.env["stock.move.line"].create(lv)    

        res = self.env.ref('stock.action_picking_tree_all')
        res = res.read()[0]
        res['domain'] = str([('id','=',picking_id.id)])   
        return  res


class CreatePickingline(models.TransientModel):
    _name = 'create.picking.line'

    cpicking_id     = fields.Many2one('create.picking',string='CPICKING',)
    product_id      = fields.Many2one('product.product',string='Product',)
    description     = fields.Char(string='Description',)
    qty             = fields.Float(string='Quantity', default=1,)
    uom             = fields.Many2one('uom.uom',string='Unit of Measure')
    include         = fields.Boolean(' ')
    request_line_id = fields.Many2one('material.request.line',string='Material request line',)
    