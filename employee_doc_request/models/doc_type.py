# -*- coding: utf-8 -*-


from odoo import models, fields,api,_

class DocType(models.Model):
    _name = 'doc.type'
    _description = 'Document Request type'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name            =  fields.Char(string='Document type',index=True)
    visibility_type =  fields.Selection([('all_department','All department'),('specific_department','Specific department')],required=True, default='all_department') 
    department_id   =  fields.Many2one('hr.department',string='Department',required=False,copy=True,)
    company_id          = fields.Many2one('res.company', string='Company', required=True,default=lambda self: self.env.company)

    @api.onchange('visibility_type')
    def _onchange_visibility_type(self):
        if self.visibility_type=='all_department':
            self.department_id = False

