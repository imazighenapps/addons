# -*- coding: utf-8 -*-


import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)


class DashboardConfig(models.Model):
    _name = 'dashboard.config'
    _description = 'Dashboard Config'
     
      
    name            = fields.Char(string="Name")
    active          = fields.Boolean(string="Active", default='True')
    nemu_name       = fields.Char(string="Menu name")
    menu_sequence   = fields.Integer('Menu sequence',default=10)
    menu_parent	    = fields.Many2one('ir.ui.menu', string='Menu Parent')
    items_ids       = fields.One2many('dashboard.item', 'dashboard_id', string='Items')
    menu_id         = fields.Many2one('ir.ui.menu', string='Menu')   
    action_id       = fields.Many2one('ir.actions.client', string='Action')       
                       

    @api.onchange('name')
    def _onchange_name(self):
        self.nemu_name = self.name
        self.menu_parent = self.env.ref('fs_dashboard.dashboard_root',False)


    @api.model
    def create(self, vals):
        res = super(DashboardConfig, self).create(vals)   
        action  = self.env['ir.actions.client'].sudo().create({
                'name': vals['name'] + " Action",   
                'tag': 'dashboard_show',
                'params': {'dashboard_id': res.id},
            })

        menu_id = self.env['ir.ui.menu'].sudo().create({
                'name': vals['nemu_name'],
                'active': vals.get('active'),
                'parent_id': vals['menu_parent'],
                'action': 'ir.actions.client,%d' % (action.id,), 
            })

        res['menu_id'] = menu_id
        res['action_id'] = action
        return res    


    def write(self, vals):
        if 'name' in vals:
            self.menu_id.name = vals['name']
            self.action_id.name = vals['name']
            
        return super().write(vals)    

    def unlink(self):
        self.menu_id.unlink()
        self.action_id.unlink()
        return super().unlink()    

