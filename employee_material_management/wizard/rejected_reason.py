# -*- coding: utf-8 -*-

from odoo import models, fields,api

class RejectedReason(models.TransientModel):
    _name = 'rejected.reason'

    name  = fields.Char('Reason')


    def do_reject(self):
        line_val = {"request_id"    : self.env.context.get('active_id'),
                    "state"         :"rejected",   
                    "employee_id"   : self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).id,
                    "date"          : fields.Date.today(),
                    "reason"        :self.name,
        }
        self.env['material.request.approval'].create(line_val)
        self.env['material.request'].search([('id','=',self.env.context.get('active_id'))]).write({'state':'rejected'}) 


