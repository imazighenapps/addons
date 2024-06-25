# -*- coding: utf-8 -*-


import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)
from . import icons

ICONS = icons.icons.sort()




class DashboardItem(models.Model):
    _name = 'dashboard.item'
    _description = 'Dashboard item'
   
    
    name          = fields.Char(string="Name")
    dashboard_id  = fields.Many2one('dashboard.config', string='Dashboard')
    model_id      = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade',
                                  domain="[('access_ids','!=',False),('transient','=',False),('model','not ilike','base_import%'),('model','not ilike','ir.%'),('model','not ilike','web_editor.%'),('model','not ilike','web_tour.%'),('model','!=','mail.thread'),('model','not ilike','dash%')]"
                                  )
    domain        = fields.Char(string="Domain",default="[]")
    item_type          = fields.Selection([('tile', 'Tile'),('bar', 'Bar Chart'),('line', 'line Chart'),('pie', 'Pie Chart'),('radar', 'Radar Chart'),
                                        ('polarArea', 'PolarArea Chart'),('doughnut', 'Doughnut Chart')], required=True,string="Type",default="tile")

    count_type     = fields.Selection([('count', 'Count'),('sum', 'Sum'),('average', 'Average')], string="Record Type", default="sum")
    count_field    = fields.Many2one('ir.model.fields',
                                        domain="[('model_id','=',model_id),('name','!=','idd'),'|','|',('ttype','=','integer'),('ttype','=','float'),('ttype','=','monetary')]",
                                        string="Record Field")
    tile_color_from =  fields.Char(string="Tile Color", help='Color of Tile From')
    tile_color_to = fields.Char(string="Tile Color", help='Color of Tile To')

    text_color      = fields.Char(string="Text Color", help='Text Color of Tile')
    fa_icon         = fields.Selection(icons.icons, string="Fa Icon", help='Icon of Tile')                         
    model_name      = fields.Char(related='model_id.model', readonly=True)

    measure_id      = fields.Many2one('ir.model.fields',
                                        domain="[('model_id','=',model_id),('name','!=','idd'),'|','|',('ttype','=','integer'),('ttype','=','float'),('ttype','=','monetary')]",
                                        string="Measure")
    group_by_field  =   fields.Many2one('ir.model.fields',
                                        domain="[('model_id','=',model_id),('name','!=','id'),'|',"
                                                           "'|','|',('ttype','=','many2one'),('ttype','=','selection'),('ttype','=','date'),('ttype','=','datetime')]",

                                        string="Group By")                                  
    
    date_group      =  fields.Selection([('day', 'Day'),('month', 'Month'),('year', 'Year')], string="Date group")
    show_date_group =  fields.Boolean()       


    @api.onchange('group_by_field')
    def _onchange_group_by_field(self):
        self.show_date_group = False
        _logger.warning('\n ok ok self.group_by_field.ttype=>%s',self.group_by_field.ttype)
        if self.group_by_field.ttype in ('date','datetime'):
            self.show_date_group = True
        