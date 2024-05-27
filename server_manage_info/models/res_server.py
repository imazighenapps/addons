# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class ResResver(models.Model):
    _name = 'res.server'
    _inherit = ['mail.thread', 'mail.activity.mixin',]
    _description = 'Server'

    name                = fields.Char(string='Nom de serveur')
    public_ip           = fields.Char('public IP') 
    vpn_ip              = fields.Char('VPN IP')
    locale_ip           = fields.Char('locale IP')
    service_ids         = fields.Many2many(string="Services",comodel_name="res.service",compute='get_service_ids',)
    server_users_ids    = fields.One2many(string="Server users",comodel_name="server.users",inverse_name='server_id')
    state               = fields.Selection([('draft', 'Draft'),('in_service', 'In service'),
                                            ('out_of_order', 'Out of order'),('under_maintenance', 'Under maintenance'),
                                            ], string='Etat', default='draft' ,group_expand='_expand_states')    

    server_type            = fields.Selection([('physical_machines', 'Physical Machines'),('virtual_machines','Virtual Machines')], string='Server Type',required=True,default="virtual_machines")   
    authorized_users_ids   = fields.Many2many(string="Authorized users",comodel_name="res.users",)
    parent_id              = fields.Many2one('res.server', string='Parent server', index=True, domain="[('server_type', '=', 'physical_machines')]")
    child_ids              = fields.One2many('res.server', 'parent_id', string='VM')
    count_childs           = fields.Integer(string='VM count',compute="compute_childs")


    def compute_childs(self):
        for rec in self:
            rec.count_childs = len(rec.child_ids)


    def do_show_childs(self):
        self.ensure_one()
        return {
           'name': 'Virtual Machines',
            'view_mode': 'kanban,tree,form',
            'res_model': 'res.server',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.child_ids.ids)],
            'context': {'default_server_type':'virtual_machines'}
        }





    def get_service_ids(self,):
        for record in self :
            service_ids = []
            record.service_ids = False 
            _logger.warning('\n ok ok record.server_users_ids=>%s',record.server_users_ids)
            for server_users in record.server_users_ids:
                if server_users.service_id.id not in service_ids:
                    service_ids.append(server_users.service_id.id)
            if len(service_ids)==0:     
                record.service_ids = False   
            else:
                 record.service_ids =service_ids       
                
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

   