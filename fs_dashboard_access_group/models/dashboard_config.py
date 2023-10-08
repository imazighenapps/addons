# -*- coding: utf-8 -*-


import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)


class DashboardConfig(models.Model):
    _inherit = 'dashboard.config'
  
     
      

    group_id         = fields.Many2one('res.groups', string='Group')   
   
 
    @api.model
    def create(self, vals):
        res = super(DashboardConfig, self).create(vals)  
        if vals['group_id']:
            res.menu_id.groups_id =  [vals['group_id']]
        return res   
    


    def write(self, vals):
        if 'group_id' in vals:
           self.menu_id.groups_id =  [vals['group_id']]
        return super().write(vals)   